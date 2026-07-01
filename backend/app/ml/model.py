"""PyTorch model architecture for the RecGym Hybrid CNN + Dilated Self-Attention.

Ported verbatim from the training notebook (Hybrid_CNN_PyTorch) so that the saved
`state_dict` (`model_weights.pt`) loads exactly. Do NOT change layer names, shapes,
or hyperparameters — they must match the checkpoint keys.

Input : (N, 1, 80, 7)  — 80 timesteps, 7 channels [A_x,A_y,A_z,G_x,G_y,G_z,C_1]
Output: (N, 12)        — raw class logits
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class MHABlock(nn.Module):
    """Multi-head self-attention (key_dim=8, num_heads=4) with residual skip."""

    def __init__(self, input_dim, key_dim=8, num_heads=4, attn_dropout=0.1):
        super().__init__()
        inner_dim = key_dim * num_heads  # 32
        self.num_heads = num_heads
        self.key_dim = key_dim
        self.scale = key_dim ** -0.5

        self.ln = nn.LayerNorm(input_dim, eps=1e-6)
        self.Wq = nn.Linear(input_dim, inner_dim)
        self.Wk = nn.Linear(input_dim, inner_dim)
        self.Wv = nn.Linear(input_dim, inner_dim)
        self.Wo = nn.Linear(inner_dim, input_dim)
        self.attn_drop = nn.Dropout(attn_dropout)
        self.out_drop = nn.Dropout(0.3)

    def forward(self, x):
        residual = x
        x = self.ln(x)
        B, T, _ = x.shape
        Q = self.Wq(x).view(B, T, self.num_heads, self.key_dim).transpose(1, 2)
        K = self.Wk(x).view(B, T, self.num_heads, self.key_dim).transpose(1, 2)
        V = self.Wv(x).view(B, T, self.num_heads, self.key_dim).transpose(1, 2)
        attn = (Q @ K.transpose(-2, -1)) * self.scale
        attn = self.attn_drop(torch.softmax(attn, dim=-1))
        out = (attn @ V).transpose(1, 2).reshape(B, T, -1)
        out = self.out_drop(self.Wo(out))
        return out + residual


class ConvBlock(nn.Module):
    """Temporal Conv2D -> Depthwise Conv2D -> Pointwise Conv2D. Output: (N, F2, 80, 1)."""

    def __init__(self, F1, D, kernLength, in_chans, dropout=0.1):
        super().__init__()
        F2 = F1 * D
        self.conv1 = nn.Conv2d(1, F1, (kernLength, 1), padding="same", bias=True)
        self.ln1 = nn.LayerNorm(F1)
        self.dw = nn.Conv2d(F1, F2, (1, in_chans), groups=F1, bias=True)
        self.ln2 = nn.LayerNorm(F2)
        self.drop1 = nn.Dropout(dropout)
        self.conv3 = nn.Conv2d(F2, F2, (10, 1), padding="same", bias=True)
        self.ln3 = nn.LayerNorm(F2)
        self.drop2 = nn.Dropout(dropout)

    def forward(self, x):
        x = self.conv1(x)
        x = F.elu(self.ln1(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2))
        x = self.dw(x)
        x = self.drop1(F.elu(self.ln2(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)))
        x = self.conv3(x)
        x = self.drop2(F.elu(self.ln3(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)))
        return x


class CausalConv1d(nn.Module):
    def __init__(self, in_ch, out_ch, kernel_size, dilation=1):
        super().__init__()
        self.pad_len = dilation * (kernel_size - 1)
        self.conv = nn.Conv1d(in_ch, out_ch, kernel_size, dilation=dilation, bias=True)
        nn.init.kaiming_uniform_(self.conv.weight, nonlinearity="linear")

    def forward(self, x):
        x = F.pad(x, (self.pad_len, 0))
        return self.conv(x)


class DIBlock(nn.Module):
    """Two-stage dilated TCN (dilation 1 -> 2), channels-first (N, C, T)."""

    def __init__(self, in_channels, filters, kernel_size, dropout, activation="elu"):
        super().__init__()
        Act = nn.ELU if activation == "elu" else nn.ReLU

        self.s1_conv1 = CausalConv1d(in_channels, filters, kernel_size, dilation=1)
        self.s1_bn1 = nn.BatchNorm1d(filters)
        self.s1_act1 = Act()
        self.s1_drop1 = nn.Dropout(dropout)
        self.s1_conv2 = CausalConv1d(filters, filters, kernel_size, dilation=1)
        self.s1_bn2 = nn.BatchNorm1d(filters)
        self.s1_act2 = Act()
        self.s1_drop2 = nn.Dropout(dropout)
        self.use_res1x1 = in_channels != filters
        if self.use_res1x1:
            self.res_conv = nn.Conv1d(in_channels, filters, 1, bias=True)
        self.s1_act_out = Act()

        self.s2_conv1 = CausalConv1d(filters, filters, kernel_size, dilation=2)
        self.s2_bn1 = nn.BatchNorm1d(filters)
        self.s2_act1 = Act()
        self.s2_drop1 = nn.Dropout(dropout)
        self.s2_conv2 = CausalConv1d(filters, filters, kernel_size, dilation=2)
        self.s2_bn2 = nn.BatchNorm1d(filters)
        self.s2_act2 = Act()
        self.s2_drop2 = nn.Dropout(dropout)
        self.s2_act_out = Act()

    def forward(self, x):
        out = self.s1_drop1(self.s1_act1(self.s1_bn1(self.s1_conv1(x))))
        out = self.s1_drop2(self.s1_act2(self.s1_bn2(self.s1_conv2(out))))
        res = self.res_conv(x) if self.use_res1x1 else x
        out = self.s1_act_out(out + res)
        s2 = self.s2_drop1(self.s2_act1(self.s2_bn1(self.s2_conv1(out))))
        s2 = self.s2_drop2(self.s2_act2(self.s2_bn2(self.s2_conv2(s2))))
        out = self.s2_act_out(s2 + out)
        return out


class PostFusion(nn.Module):
    """Dual-branch CNN -> per-window GRU + MHA + TCN -> averaged logits."""

    def __init__(self, n_classes=12, in_chans=7, in_samples=80, n_windows=4,
                 F1=16, D=2, kernelSize=64, dropout=0.1,
                 di_kernelSize=4, di_filters=32, di_dropout=0.3,
                 di_activation="elu"):
        super().__init__()
        self.n_windows = n_windows
        F2 = F1 * D
        concat_dim = F2 * 2

        self.conv_imu = ConvBlock(F1, D, kernelSize, in_chans=6, dropout=dropout)
        self.conv_cap = ConvBlock(F1, D, kernelSize, in_chans=1, dropout=dropout)

        self.gru_blocks = nn.ModuleList([
            nn.GRU(input_size=concat_dim, hidden_size=128, num_layers=1,
                   batch_first=True, dropout=0.0)
            for _ in range(n_windows)
        ])
        self.mha_blocks = nn.ModuleList([MHABlock(128) for _ in range(n_windows)])
        self.di_blocks = nn.ModuleList([
            DIBlock(128, di_filters, di_kernelSize, di_dropout, di_activation)
            for _ in range(n_windows)
        ])
        self.output_denses = nn.ModuleList([
            nn.Linear(di_filters, n_classes) for _ in range(n_windows)
        ])

    def forward(self, x):
        # x: (N, 1, 80, 7)
        x_imu = x[:, :, :, 0:6]
        x_cap = x[:, :, :, -1:]

        b_imu = self.conv_imu(x_imu)
        b_cap = self.conv_cap(x_cap)

        block1 = torch.cat([b_imu, b_cap], dim=1).squeeze(-1).permute(0, 2, 1)

        T = block1.shape[1]
        sw_outputs = []
        for i in range(self.n_windows):
            st = i
            end = T - self.n_windows + i + 1
            win = block1[:, st:end, :]
            win, _ = self.gru_blocks[i](win)
            win = self.mha_blocks[i](win)
            win = win.permute(0, 2, 1)
            win = self.di_blocks[i](win)
            win = win[:, :, -1]
            sw_outputs.append(self.output_denses[i](win))

        return torch.stack(sw_outputs, dim=0).mean(dim=0)


def build_model(n_classes: int = 12, in_chans: int = 7, in_samples: int = 80) -> PostFusion:
    """Instantiate PostFusion with the author's exact hyperparameters."""
    return PostFusion(
        n_classes=n_classes,
        in_chans=in_chans,
        in_samples=in_samples,
        n_windows=4,
        F1=32,
        D=4,
        kernelSize=20,
        dropout=0.1,
        di_kernelSize=3,
        di_filters=32,
        di_dropout=0.1,
        di_activation="elu",
    )
