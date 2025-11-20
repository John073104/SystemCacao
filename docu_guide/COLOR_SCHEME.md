# 🎨 CacaoGuard System Color Scheme

## Primary Brand Colors

### 🟤 Cacao Brown / Amber (Primary Theme)
| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| Amber 50 | `#fef3e2` | `bg-amber-50` | Light backgrounds, highlights |
| Amber 100 | `#fef3c7` | `bg-amber-100` | Badges, light accents |
| Amber 400 | `#fbbf24` | `text-amber-400` | Icons, store icon |
| Amber 500 | `#f59e0b` | `bg-amber-500` | Primary buttons, accents |
| Amber 600 | `#d97706` | `bg-amber-600` | Primary button hover |
| Amber 700 | `#b45309` | `text-amber-700` | Dark text accents |
| Amber 800 | `#92400e` | `text-amber-800` | Darker text |

**Purpose:** Main brand color representing cacao/chocolate theme. Used for marketplace, products, and primary actions.

---

## Status Colors

### 🟢 Success / Green
| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| Green 50 | `#f0fdf4` | `bg-green-50` | Success backgrounds |
| Green 100 | `#dcfce7` | `bg-green-100` | Success badges, delivered status |
| Green 400 | `#4ade80` | `bg-green-400` | Online indicator dot |
| Green 500 | `#10b981` | `bg-green-500` | Success buttons, delivered |
| Green 600 | `#059669` | `bg-green-600` | Success hover, confirm |
| Green 700 | `#047857` | `bg-green-700` | Dark success |
| Green 800 | `#065f46` | `text-green-800` | Success text |

**Specific Shades:**
- `#48bb78` - Farm location buttons
- `#d1fae5` - Light success background
- `#a7f3d0` - Success border

**Purpose:** Completed orders, delivered status, success messages, confirmation buttons.

---

### 🔵 Information / Blue
| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| Blue 50 | `#eff6ff` | `bg-blue-50` | Info backgrounds, notifications |
| Blue 100 | `#dbeafe` | `bg-blue-100` | Info badges, active states |
| Blue 500 | `#3b82f6` | `bg-blue-500` | Info buttons, confirmed status |
| Blue 600 | `#2563eb` | `bg-blue-600` | Primary action buttons |
| Blue 700 | `#1d4ed8` | `bg-blue-700` | Button hover |

**Specific Shades:**
- `#667eea` - Admin gradient start
- `#4facfe` - Light blue gradient
- `#00f2fe` - Cyan gradient end
- `#3498db` - Loading spinner
- `#06b6d4` - Cyan accent
- `#0891b2` - Dark cyan
- `#e0f2fe` - Very light blue background

**Purpose:** Information messages, confirmed orders, primary actions, navigation highlights.

---

### 🟡 Warning / Yellow
| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| Yellow 100 | `#fef3c7` | `bg-yellow-100` | Warning backgrounds |
| Yellow 800 | `#854d0e` | `text-yellow-800` | Warning text |

**Purpose:** Pending orders, warnings, attention-needed items.

---

### 🔴 Error / Red
| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| Red 50 | `#fef2f2` | `bg-red-50` | Error backgrounds |
| Red 100 | `#fee2e2` | `bg-red-100` | Error badges |
| Red 500 | `#ef4444` | `bg-red-500` | Error buttons, cancelled |
| Red 800 | `#991b1b` | `text-red-800` | Error text |

**Specific Shades:**
- `#e53e3e` - Danger buttons
- `#fecaca` - Light red border

**Purpose:** Cancelled orders, errors, delete actions, critical warnings.

---

## Neutral Colors (Gray Scale)

| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| Gray 50 | `#f9fafb` | `bg-gray-50` | Light backgrounds, table headers |
| Gray 100 | `#f3f4f6` | `bg-gray-100` | Body background, cards |
| Gray 200 | `#e5e7eb` | `bg-gray-200` | Borders, dividers |
| Gray 300 | `#d1d5db` | `border-gray-300` | Input borders |
| Gray 400 | `#9ca3af` | `text-gray-400` | Placeholder text |
| Gray 500 | `#6b7280` | `bg-gray-500` | Secondary buttons |
| Gray 600 | `#4b5563` | `bg-gray-600` | Dark buttons |
| Gray 700 | `#374151` | `text-gray-700` | Body text |
| Gray 800 | `#1f2937` | `text-gray-800` | Headings |
| Gray 900 | `#111827` | `text-gray-900` | Dark text |

**Purpose:** Backgrounds, text, borders, neutral UI elements.

---

## Special Accent Colors

### 🟣 Purple
| Color Name | Hex Code | Tailwind Class | Usage |
|------------|----------|----------------|-------|
| Purple 50 | `#f3e8ff` | `bg-purple-50` | Light purple bg |
| Purple 400 | `#a855f7` | `bg-purple-400` | Purple accent |
| Purple 500 | `#8b5cf6` | `bg-purple-500` | Purple primary |
| Purple 600 | `#7c3aed` | `bg-purple-600` | Purple hover |

**Specific Shades:**
- `#764ba2` - Admin gradient end
- `#d946ef` - Magenta gradient

**Purpose:** Processing status, dashboard gradients, chart colors.

---

### 🎨 Additional Gradient Colors

**Pink/Rose:**
- `#fa709a` - Pink gradient start
- `#fee140` - Yellow gradient end
- `#ff9a9e` - Light pink
- `#fecfef` - Very light pink
- `#a8edea` - Mint
- `#fed6e3` - Light pink

**Green Gradients:**
- `#43e97b` - Bright green
- `#38f9d7` - Turquoise

**Orange:**
- `#f97316` - Orange accent

**Purpose:** Dashboard cards, chart visualizations, decorative gradients.

---

## Sidebar / Navigation Colors

### Dark Sidebar (Admin)
| Element | Hex Code | Tailwind Class |
|---------|----------|----------------|
| Background | `#1e293b` / `#0f172a` | Gradient dark slate |
| Active Border | `#3b82f6` | Blue 500 |
| Text | White | `text-white` |
| Icons | Various colors | Context-dependent |

**Purpose:** Professional dark theme for admin dashboard.

---

## Background Gradients

### User Dashboard Background
```css
background: linear-gradient(135deg, #fef3e2 0%, #f3e8ff 50%, #e0f2fe 100%);
```
Amber → Purple → Blue gradient for warm, welcoming feel.

### Admin Dashboard Background
```css
background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
```
Light gray gradient for professional look.

### Header/Hero Gradients
```css
/* Green User Header */
background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);

/* Orange Admin Header */
background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
```

---

## Status Badge Color Mapping

| Status | Background | Text | Usage |
|--------|------------|------|-------|
| **Pending** | `bg-yellow-100` | `text-yellow-800` | Orders waiting |
| **Confirmed** | `bg-blue-100` | `text-blue-800` | Processing orders |
| **Delivered** | `bg-green-100` | `text-green-800` | Complete orders |
| **Cancelled** | `bg-red-100` | `text-red-800` | Cancelled orders |
| **Default** | `bg-gray-100` | `text-gray-800` | Unknown status |

---

## Button Color Guidelines

### Primary Actions
- **Background:** `bg-green-600` / `bg-blue-600` / `bg-amber-600`
- **Hover:** `hover:bg-green-700` / `hover:bg-blue-700` / `hover:bg-amber-700`
- **Text:** `text-white`

### Secondary Actions
- **Background:** `bg-gray-200`
- **Hover:** `hover:bg-gray-300`
- **Text:** `text-gray-800`

### Danger Actions
- **Background:** `bg-red-500`
- **Hover:** `hover:bg-red-600`
- **Text:** `text-white`

---

## Icon Color Gradients

Used for dashboard stat cards:

1. **Purple Gradient:** `#667eea` → `#764ba2`
2. **Cyan Gradient:** `#4facfe` → `#00f2fe`
3. **Green Gradient:** `#43e97b` → `#38f9d7`
4. **Pink Gradient:** `#fa709a` → `#fee140`
5. **Rose Gradient:** `#ff9a9e` → `#fecfef`
6. **Mint Gradient:** `#a8edea` → `#fed6e3`

---

## Accessibility Notes

### Text Contrast Ratios
- ✅ **Dark text on light backgrounds:** Gray 700+ on White/Gray 50
- ✅ **Light text on dark backgrounds:** White on Gray 800+
- ✅ **Colored text on colored backgrounds:** Always check WCAG AA compliance

### Color Blind Friendly
- Use **icons + text** for status (not just color)
- Avoid red/green only combinations
- Include patterns or shapes with colors

---

## Usage Guidelines

### DO's ✅
- Use **Amber** for marketplace and product features
- Use **Green** for success, completion, growth (farms)
- Use **Blue** for information, navigation, primary actions
- Use **Gray** for neutral UI, text, borders
- Maintain consistent color → meaning mapping

### DON'Ts ❌
- Don't mix too many bright colors in one view
- Don't use color as the only indicator
- Don't use red/green together without additional cues
- Don't override status colors (confuses users)

---

## Quick Reference Chart

| Feature | Primary Color | Accent Color |
|---------|--------------|--------------|
| **Marketplace** | Amber 600 | Amber 800 |
| **Orders** | Blue 600 | Green 100 (delivered) |
| **Disease Detection** | Green 600 | Red 500 (disease found) |
| **Farm Mapping** | Green 500 | Cyan 600 |
| **Admin Dashboard** | Slate/Gray | Purple gradients |
| **User Dashboard** | Amber + Purple | Green accents |
| **Authentication** | Blue 600 | Gray 700 |

---

## Export for Design Tools

### Figma / Adobe XD Color Palette

**Primary:**
- `#f59e0b` (Amber 500)
- `#10b981` (Green 500)
- `#3b82f6` (Blue 500)

**Secondary:**
- `#6b7280` (Gray 500)
- `#ef4444` (Red 500)
- `#eab308` (Yellow 500)

**Neutral:**
- `#ffffff` (White)
- `#f9fafb` (Gray 50)
- `#111827` (Gray 900)

---

## Version History
- **v1.0** - Initial color scheme documentation
- **Date:** November 2025
- **System:** CacaoGuard Disease Detection & E-commerce Platform
