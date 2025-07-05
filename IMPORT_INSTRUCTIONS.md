# 🔄 Collection Update Instructions

## Option 1: Manual Export from Moxfield (Recommended)

Since your collection appears to be private, please follow these steps:

### Step 1: Export Your Collection
1. **Go to your collection**: https://moxfield.com/collection/tVocckRgh06E-v0c5VY9JA
2. **Login to Moxfield** if you aren't already
3. **Find the Export button** (usually in the top right or in a menu)
4. **Select "CSV" format**
5. **Download the file** (it will likely be named something like "collection.csv")

### Step 2: Import to MyManaBox
Once you have the CSV file downloaded:

```bash
# Option A: Rename the file and place it in the project directory
# Rename your downloaded file to "moxfield_export.csv" and put it in:
# C:\Users\Petro\repos\MyManaBox\

# Option B: Use the import command with your downloaded file
python card_sorter.py --import-file "path\to\your\downloaded\file.csv"

# Example:
python card_sorter.py --import-file "C:\Users\Petro\Downloads\collection.csv"
```

### Step 3: Verify the Import
After importing, run:
```bash
python mymanabox.py --summary
```

## Option 2: Make Collection Public (Alternative)

If you want to make the collection public for automatic import:

1. Go to https://moxfield.com/collection/tVocckRgh06E-v0c5VY9JA
2. Look for privacy/sharing settings
3. Change from "Private" to "Public"
4. Then run: `python card_sorter.py --import-url "https://moxfield.com/collection/tVocckRgh06E-v0c5VY9JA"`

## What Happens During Import

✅ **Automatic Backup**: Your current collection will be backed up before import
✅ **Complete Replacement**: The new collection will completely replace your current one
✅ **Immediate Summary**: You'll see a summary of the imported collection
✅ **Full Functionality**: All MyManaBox features will work with the new collection

## After Import

Once your collection is imported, you can use all MyManaBox features:

```bash
# View collection summary
python mymanabox.py --summary

# Search for cards
python mymanabox.py --search "Lightning Bolt"

# Find duplicates
python mymanabox.py --duplicates

# Sort and export
python mymanabox.py --sort color

# Enhanced features with API
python mymanabox.py --enhanced --mana-curve
```

## Need Help?

If you encounter any issues:
1. Make sure the CSV file contains columns like "Count", "Name", "Edition"
2. Check that the file path is correct
3. Ensure you have write permissions in the project directory

Your collection will be completely updated and ready to use! 🎉
