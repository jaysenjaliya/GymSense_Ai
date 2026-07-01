// Curated fitness imagery (Unsplash). A gradient overlay always sits on top so the
// UI stays readable even if an image is slow to load.
const u = (id, w = 1400) =>
  `https://images.unsplash.com/${id}?auto=format&fit=crop&w=${w}&q=80`;

export const IMAGES = {
  heroAthlete: u("photo-1534438327276-14e5300c3a48", 1600),
  gymInterior: u("photo-1540497077202-7c8a3999166f"),
  dumbbells: u("photo-1517836357463-d25dfeac3438", 1000),
  running: u("photo-1571008887538-b36bb32f4571", 1000),
  barbell: u("photo-1534368420009-621bfab424a8", 1000),
  kettlebell: u("photo-1517963879433-6ad2b056d712", 1000),
  authSide: u("photo-1550345332-09e3ac987658", 1200),
  uploadHero: u("photo-1526506118085-60ce8714f8c5", 1000),
};

// Auth / marketing background used behind glass panels.
export const AUTH_BG = IMAGES.authSide;
