# MTG Collection Manager - Claude Project Guide

**How to use this project in Claude Projects for maximum efficiency**

---

## 🎯 What is a Claude Project?

Claude Projects let you create a dedicated workspace with:
- **Custom knowledge**: Upload your specific files and documentation
- **Persistent context**: Claude remembers project details across conversations
- **Organized workspace**: Keep all MTG-related work in one place
- **Enhanced capabilities**: Access to tools and integrations

---

## 🚀 Setting Up This Project in Claude

### Step 1: Create the Project

1. **In Claude.ai**, click **Projects** (left sidebar)
2. Click **Create Project**
3. Name it: `MTG Collection Manager`
4. Description: `5000+ card cataloging system with Scryfall, ManaBox, and Moxfield integration`

### Step 2: Upload Project Files

Upload these key files to provide Claude with context:

**Essential Documentation:**
```
✅ README.md
✅ docs/API_INTEGRATION.md
✅ docs/WORKFLOWS.md
✅ config/settings.json
```

**Source Code (as needed):**
```
✅ src/catalogue.py
✅ src/api_clients/scryfall.py
✅ scripts/consolidate_manabox.py
✅ scripts/enrich_collection.py
```

**Your Data (after collecting):**
```
📊 data/exports/consolidated_collection.csv
📊 exports/moxfield_import.csv
📋 Collection statistics and reports
```

### Step 3: Add Project Instructions

In **Project Instructions**, add this custom knowledge:

```
This project manages a ~5000+ card Magic: The Gathering collection using:

**Current Status:**
- Collection size: [UPDATE AS YOU SCAN]
- Platform sync: ManaBox → Local DB → Moxfield
- Pricing source: Scryfall (primary), TCGPlayer (optional)

**Key Commands:**
- Import: python src/catalogue.py --import [file]
- Enrich: python scripts/enrich_collection.py --update-prices
- Export: python src/catalogue.py --export [file] --format moxfield
- Stats: python src/catalogue.py --stats

**Workflows:**
1. Scan cards in ManaBox (mobile)
2. Export CSV from ManaBox
3. Consolidate CSVs: python scripts/consolidate_manabox.py
4. Import to local DB
5. Enrich with Scryfall data
6. Export to Moxfield

**Priority Cards:**
- [Add your specific high-value cards]
- [Add your active deck lists]
- [Add your wishlist]

**Custom Preferences:**
- Default condition: NM
- Preferred scanning batches: 100-200 cards
- Price update frequency: Weekly
```

---

## 💡 How to Use Claude with This Project

### For Scanning Sessions

**Before scanning:**
```
Me: I'm about to scan 200 cards from Kamigawa: Neon Dynasty. 
    Any tips for this set specifically?

Claude: [Provides set-specific scanning advice, common issues, 
        price highlights for NEO]
```

**After scanning:**
```
Me: Just exported manabox_session_3.csv with 187 cards. 
    Walk me through consolidation and import.

Claude: [Provides step-by-step commands with your specific filename]
```

### For Data Analysis

```
Me: Show me my most valuable cards by set

Claude: [Generates SQL query, runs analysis, formats results]
```

```
Me: Which cards should I prioritize for protective sleeves?

Claude: [Analyzes collection, suggests cards >$X value]
```

### For Deck Building

```
Me: I want to build a Kaalia deck. Check what I already own 
    from the popular Kaalia lists.

Claude: [Fetches Kaalia primer, cross-references your collection,
        generates shopping list]
```

### For Troubleshooting

```
Me: Getting error "IntegrityError" when importing. Here's my CSV...

Claude: [Analyzes CSV format, identifies issue, provides fix]
```

---

## 🔧 Project Customization Tips

### Add Your Deck Lists

Create a **Decks** section in Project Instructions:

```
**Active Decks:**
1. Kaalia Voltron (Commander)
   - Priority missing: [list]
   - Budget: $500 remaining
   
2. Yuriko Ninjas (Commander)
   - Status: Complete
   - Optimization targets: Faster mana base
   
3. Mono-Red Goblins (Modern)
   - Sideboard needs: 5 cards
```

### Track Your Goals

```
**Collection Goals:**
- [ ] Catalog all 5000+ cards (current: 0/5000)
- [ ] Complete Kaalia deck (current: 68/100 cards)
- [ ] Reach $15,000 collection value (current: $0)
- [ ] Trade surplus bulk for modern staples
```

### Save Common Queries

Create custom commands in Project Instructions:

```
**Custom Commands:**
- "weekly update" = Run price updates, generate reports, check value changes
- "deck check [name]" = Analyze deck, suggest upgrades, check owned cards
- "trade prep" = Generate trade binder, update buylist prices
```

---

## 🤝 Working with Claude Iteratively

### Multi-Session Workflows

**Session 1: Planning**
```
Me: I have 5000 cards to catalog. Help me create a realistic timeline.

Claude: [Creates week-by-week plan with milestones]
```

**Session 2: Execution** (next day)
```
Me: Continue with the scanning workflow we discussed.

Claude: [Remembers the plan, provides next steps]
```

**Session 3: Optimization** (week later)
```
Me: The scanning is slower than expected. Optimize the process.

Claude: [Suggests improvements based on previous sessions]
```

### Progressive Enhancement

Start simple, add complexity:

**Week 1:** Basic scanning and import
**Week 2:** Add price tracking
**Week 3:** Set up deck analysis
**Week 4:** Add automated exports
**Week 5:** Build custom scripts

Claude can guide you through each phase.

---

## 📊 Tracking Progress in the Project

Update your Project Instructions regularly:

```markdown
**Progress Log:**

2025-12-25: Project initialized
- Database created
- Scryfall API tested
- First 100 cards scanned

2025-12-26: Session 1 complete
- Scanned: 187 cards (Kamigawa: Neon Dynasty)
- Total collection: 187 cards
- Errors: 3 cards (manual entry needed)

2025-12-27: Enrichment complete
- Added Scryfall data to all cards
- Total value: $342.15
- Top card: [card name] at $45.99
```

This gives Claude context for every conversation.

---

## 🎓 Advanced Project Features

### Custom Knowledge Base

Upload **reference documents** to the project:

```
📄 EDHREC top Kaalia cards (PDF)
📄 Your trade partner's wishlist (CSV)
📄 Local game store buylist (PDF)
📄 Your deck primers (Markdown)
```

Claude can cross-reference these in conversations.

### Integration with Other Tools

Link your project to external resources:

```
**External Resources:**
- Moxfield profile: https://moxfield.com/users/[your_username]
- ManaBox cloud sync: [link]
- Google Drive backup: [link]
- TCGPlayer seller account: [link]
```

### Automation Scripts

Save command aliases in Project Instructions:

```bash
# Weekly routine
alias mtg-update="
  python scripts/enrich_collection.py --update-prices && 
  python src/catalogue.py --stats && 
  python scripts/backup.py
"

# Quick deck check
alias deck-status="
  python scripts/check_missing.py --deck decks/kaalia.txt
"
```

Ask Claude to generate these for you.

---

## 🚨 Project Maintenance

### Monthly Checklist

```
**Monthly Tasks:**
- [ ] Backup database to cloud
- [ ] Update all card prices
- [ ] Review and consolidate tags
- [ ] Check for duplicate entries
- [ ] Archive old export files
- [ ] Update deck lists
```

### Quarterly Reviews

```
**Quarterly Analysis:**
- Collection value trends
- Most-added sets
- Deck completion progress
- Budget utilization
- Trading activity summary
```

Ask Claude to generate these reports automatically.

---

## 💡 Pro Tips for Claude Projects

### 1. Be Specific with Context

❌ **Vague:** "Help me with my cards"

✅ **Specific:** "I just scanned 150 cards from session 2. The export is 
manabox_session_2.csv in my Downloads. Walk me through consolidating 
this with session 1's export and importing to the database."

### 2. Reference Previous Work

✅ "Use the consolidation script we created last week"
✅ "Export using the Moxfield format from our earlier conversation"
✅ "Check against my Kaalia deck list in the project files"

### 3. Iterate on Solutions

```
Me: That SQL query works but is slow for 5000 cards.

Claude: [Optimizes with indexes, batch processing]

Me: Perfect. Now add this to the catalogue.py as a helper function.

Claude: [Implements and tests]
```

### 4. Save Successful Patterns

When you find a workflow that works:

```
Me: That consolidation process was perfect. Add it to 
    PROJECT_WORKFLOWS.md so we can reference it later.

Claude: [Documents the exact steps, creates reusable template]
```

---

## 📚 Resources

### Project Files
- **README.md** - Project overview and quick start
- **docs/API_INTEGRATION.md** - Detailed API setup
- **docs/WORKFLOWS.md** - Step-by-step task guides

### External Links
- [Scryfall API Docs](https://scryfall.com/docs/api)
- [TCGPlayer Developer Portal](https://developer.tcgplayer.com/)
- [Moxfield](https://moxfield.com)
- [ManaBox](https://manabox.app)

### Community
- EDHREC for deck ideas
- MTGGoldfish for metagame data
- Reddit r/mtgfinance for market trends

---

## 🎯 Getting Started Checklist

- [ ] Create Claude Project
- [ ] Upload essential documentation
- [ ] Add Project Instructions
- [ ] Run `python setup.py`
- [ ] Scan first 100 test cards
- [ ] Import and enrich test batch
- [ ] Verify Moxfield export works
- [ ] Set up automated backups

---

**Ready to transform your card cataloging from chaos to systematic efficiency!**

---

*Last Updated: 2025-12-25*
*Project Version: 1.0.0*
