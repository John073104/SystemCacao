# Migration Guide: Old Products to Cloudinary

## Problem
Old products uploaded before Cloudinary integration have images stored at `/media/products/xxx.jpg` paths. These files don't exist on Render, so they show as placeholders.

## Solution Options

### Option 1: Auto-Replace with Placeholder (Fastest)
**Good for:** Many products, will fix them later

```bash
python migrate_images_to_cloudinary.py
# Choose option 2
```

This will:
- Replace all `/media/` paths with placeholder
- You can later edit products in admin panel
- Upload new images (will go to Cloudinary automatically)

### Option 2: Manual Migration (Best Quality)
**Good for:** 1-10 products you want to fix now

```bash
python migrate_images_to_cloudinary.py
# Choose option 1
# Follow prompts to upload each image
```

This will:
- Ask you for image file paths
- Upload to Cloudinary
- Update Firestore with new URLs

### Option 3: Re-upload via Admin Panel (Recommended)
**Good for:** When you have time, best result

1. After adding Cloudinary env vars to Render
2. Go to admin panel on your live site
3. Edit each product
4. Re-upload the images
5. Save - images automatically go to Cloudinary!

## Which Should You Choose?

**If you have 1-5 products:**
→ Use Option 3 (Admin Panel) - easiest!

**If you have 6-20 products:**
→ Use Option 2 (Manual Migration Script) - saves time

**If you have 20+ products:**
→ Use Option 1 (Auto-Placeholder) now
→ Fix important products via admin panel later
→ Others can wait

## Current Status

After you add Cloudinary env vars to Render:
- ✅ NEW products: Images go to Cloudinary automatically
- ❌ OLD products: Still show placeholder (need migration)

## Don't Worry!
The migration script is optional. You can always:
- Just use admin panel to re-upload images
- Fix products one by one as needed
- Leave less important products with placeholder for now
