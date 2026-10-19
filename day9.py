import cv2
import numpy as np
import os

WIDTH, HEIGHT = 1080, 1920
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2 - 60

WINDOW_NAME = "Navratri Day 9 - Grand Finale"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 540, 960)
cv2.moveWindow(WINDOW_NAME, 500, 30)

def find_file_smart(keyword):
    all_files = os.listdir(".")
    for f in all_files:
        if keyword.lower() in f.lower() and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            return f
    return None

def load_avatar(keyword, target_w, target_h):
    fpath = find_file_smart(keyword)
    if not fpath:
        img = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        cv2.putText(img, keyword[:10], (10, target_h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return img

    raw = cv2.imread(fpath, cv2.IMREAD_UNCHANGED)
    if raw is None:
        return np.zeros((target_h, target_w, 3), dtype=np.uint8)

    if len(raw.shape) == 3 and raw.shape[2] == 4:
        b, g, r, a = cv2.split(raw)
        rgb = cv2.merge([b, g, r])
        alpha = (a.astype(float) / 255.0)[:, :, None]
        white_bg = np.ones_like(rgb, dtype=np.uint8) * 255
        raw = (alpha * rgb + (1.0 - alpha) * white_bg).astype(np.uint8)
    elif len(raw.shape) == 2:
        raw = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)

    return cv2.resize(raw, (target_w, target_h), interpolation=cv2.INTER_AREA)

def create_circular_icon(img, diameter):
    img_resized = cv2.resize(img, (diameter, diameter))
    mask = np.zeros((diameter, diameter), dtype=np.uint8)
    cv2.circle(mask, (diameter // 2, diameter // 2), diameter // 2 - 4, 255, -1)
    
    circular = np.zeros((diameter, diameter, 3), dtype=np.uint8)
    circular[mask == 255] = img_resized[mask == 255]
    cv2.circle(circular, (diameter // 2, diameter // 2), diameter // 2 - 4, (0, 215, 255), 5)
    cv2.circle(circular, (diameter // 2, diameter // 2), diameter // 2 - 1, (255, 255, 255), 2)
    return circular, mask

def overlay_image(bg, fg, mask, x, y):
    h, w = fg.shape[:2]
    y1, y2 = max(0, y), min(bg.shape[0], y + h)
    x1, x2 = max(0, x), min(bg.shape[1], x + w)
    fy1, fy2 = max(0, -y), min(h, bg.shape[0] - y)
    fx1, fx2 = max(0, -x), min(w, bg.shape[1] - x)

    if y1 >= y2 or x1 >= x2 or fy1 >= fy2 or fx1 >= fx2:
        return bg

    sub_bg = bg[y1:y2, x1:x2]
    sub_fg = fg[fy1:fy2, fx1:fx2]
    sub_mask = mask[fy1:fy2, fx1:fx2] / 255.0

    for c in range(3):
        sub_bg[:, :, c] = (sub_mask * sub_fg[:, :, c] + (1 - sub_mask) * sub_bg[:, :, c]).astype(np.uint8)
    bg[y1:y2, x1:x2] = sub_bg
    return bg

# --- ASSETS LOADING ---
siddhidatri_img = load_avatar("siddhidatri", 800, 800)
final_img = load_avatar("final", WIDTH, HEIGHT)

avatar_keywords = [
    "shail",       # Day 1: Shailputri
    "brahma",      # Day 2: Brahmacharini
    "chandra",     # Day 3: Chandraghanta
    "kush",        # Day 4: Kushmanda
    "skanda",      # Day 5: Skandamata
    "katya",       # Day 6: Katyayani
    "ratri",       # Day 7: Kalaratri
    "gauri"        # Day 8: Mahagauri
]

# Bigger icon size for clear visibility
ICON_SIZE = 190
avatar_icons = []
avatar_masks = []

for kw in avatar_keywords:
    img = load_avatar(kw, ICON_SIZE, ICON_SIZE)
    icon, mask = create_circular_icon(img, ICON_SIZE)
    avatar_icons.append(icon)
    avatar_masks.append(mask)

siddhi_icon, siddhi_mask = create_circular_icon(siddhidatri_img, ICON_SIZE)
all_9_icons = avatar_icons + [siddhi_icon]
all_9_masks = avatar_masks + [siddhi_mask]

# Circular Orbit radius and positions for 9 avatars
ORBIT_RADIUS = 430
angles_base = np.linspace(0, 2 * np.pi, 9, endpoint=False) - (np.pi / 2)
# Slot 8 (Day 9 position)
siddhi_target_x = int(CENTER_X + ORBIT_RADIUS * np.cos(angles_base[8]))
siddhi_target_y = int(CENTER_Y + ORBIT_RADIUS * np.sin(angles_base[8]))

TOTAL_FRAMES = 310

for frame_idx in range(TOTAL_FRAMES):
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    frame[:, :] = (18, 10, 24)

    # 1. Center Iris Reveal of Maa Siddhidatri (0 to 55)
    if frame_idx < 55:
        progress = min(1.0, frame_idx / 40.0)
        curr_r = int(progress * 380)

        if curr_r > 0:
            s_mask = np.zeros((800, 800), dtype=np.uint8)
            cv2.circle(s_mask, (400, 400), curr_r, 255, -1)
            frame = overlay_image(frame, siddhidatri_img, s_mask, CENTER_X - 400, CENTER_Y - 400)
            cv2.circle(frame, (CENTER_X, CENTER_Y), curr_r, (0, 215, 255), 5)

        cv2.putText(frame, "Navratri Special : 9/9", (CENTER_X - 240, HEIGHT - 220), cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 215, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Maa Siddhidatri | Grand Finale", (CENTER_X - 270, HEIGHT - 160), cv2.FONT_HERSHEY_DUPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

    # 2. Siddhidatri smoothly moves and scales to orbit slot (55 to 90)
    elif frame_idx < 90:
        t = (frame_idx - 55) / 35.0
        cur_x = int((1 - t) * CENTER_X + t * siddhi_target_x)
        cur_y = int((1 - t) * CENTER_Y + t * siddhi_target_y)
        cur_size = int((1 - t) * 760 + t * ICON_SIZE)

        resized_img = cv2.resize(siddhidatri_img, (cur_size, cur_size))
        cur_icon, cur_mask = create_circular_icon(resized_img, cur_size)
        frame = overlay_image(frame, cur_icon, cur_mask, cur_x - cur_size // 2, cur_y - cur_size // 2)

        cv2.putText(frame, "Navratri Special : 9/9", (CENTER_X - 240, HEIGHT - 220), cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 215, 255), 2, cv2.LINE_AA)

    # 3. Avatars Day 1 to Day 8 appear along rotating circle (90 to 180)
    elif frame_idx < 180:
        # Subtle rotation effect
        rot_angle = (frame_idx - 90) * 0.015
        revealed_count = min(8, int((frame_idx - 90) / 10) + 1)

        # Place Siddhidatri in orbit
        ang_9 = angles_base[8] + rot_angle
        p9_x = int(CENTER_X + ORBIT_RADIUS * np.cos(ang_9))
        p9_y = int(CENTER_Y + ORBIT_RADIUS * np.sin(ang_9))
        frame = overlay_image(frame, all_9_icons[8], all_9_masks[8], p9_x - ICON_SIZE // 2, p9_y - ICON_SIZE // 2)

        for i in range(revealed_count):
            ang = angles_base[i] + rot_angle
            ax = int(CENTER_X + ORBIT_RADIUS * np.cos(ang))
            ay = int(CENTER_Y + ORBIT_RADIUS * np.sin(ang))

            # Golden sunbeam connectors
            ray_layer = frame.copy()
            cv2.line(ray_layer, (CENTER_X, CENTER_Y), (ax, ay), (0, 215, 255), 5, cv2.LINE_AA)
            cv2.line(ray_layer, (CENTER_X, CENTER_Y), (ax, ay), (255, 255, 255), 2, cv2.LINE_AA)
            cv2.addWeighted(ray_layer, 0.4, frame, 0.6, 0, frame)

            frame = overlay_image(frame, all_9_icons[i], all_9_masks[i], ax - ICON_SIZE // 2, ay - ICON_SIZE // 2)

        cv2.putText(frame, "All 9 Divine Forms United", (CENTER_X - 260, HEIGHT - 180), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 215, 255), 2, cv2.LINE_AA)

    # 4. All 9 Avatars Converge into Center (180 to 225)
    elif frame_idx < 225:
        conv_t = (frame_idx - 180) / 45.0
        curr_orbit = int(ORBIT_RADIUS * (1.0 - conv_t))
        cur_icon_sz = max(28, int(ICON_SIZE * (1.0 - conv_t * 0.65)))
        rot_angle = (180 - 90) * 0.015 + conv_t * 0.5

        for i in range(9):
            ang = angles_base[i] + rot_angle
            ax = int(CENTER_X + curr_orbit * np.cos(ang))
            ay = int(CENTER_Y + curr_orbit * np.sin(ang))

            scaled_icon = cv2.resize(all_9_icons[i], (cur_icon_sz, cur_icon_sz))
            scaled_mask = cv2.resize(all_9_masks[i], (cur_icon_sz, cur_icon_sz))
            frame = overlay_image(frame, scaled_icon, scaled_mask, ax - cur_icon_sz // 2, ay - cur_icon_sz // 2)
            cv2.line(frame, (CENTER_X, CENTER_Y), (ax, ay), (0, 215, 255), 3, cv2.LINE_AA)

        # Supernova Flash
        if conv_t > 0.7:
            flash_intensity = int(255 * (conv_t - 0.7) / 0.3)
            blast_r = int((conv_t - 0.7) * 3600)
            cv2.circle(frame, (CENTER_X, CENTER_Y), blast_r, (flash_intensity, flash_intensity, 255), -1)

    # 5. Grand Reveal of Maa Jagdamba (final.jpg) (225 to 310)
    else:
        fade_t = min(1.0, (frame_idx - 225) / 20.0)
        frame = cv2.addWeighted(final_img, fade_t, np.zeros_like(final_img), 1 - fade_t, 0)

        cv2.putText(frame, "OM JAYO JAYO MAA JAGDAMBE", (CENTER_X - 330, HEIGHT - 200), cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 215, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "The Supreme Cosmic Source", (CENTER_X - 220, HEIGHT - 140), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow(WINDOW_NAME, frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cv2.waitKey(3000)
cv2.destroyAllWindows()