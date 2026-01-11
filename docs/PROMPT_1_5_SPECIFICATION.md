# PROMPT 1.5: Integration Testing & Refinement

**Status**: In Progress  
**Phase**: Phase 1 Foundation - Final Integration & Testing  
**Target Completion**: Current Session  
**Success Criteria**: Phase 1 reaches 75% (70% → 75%)  
**Estimated Duration**: 90 minutes

---

## Objectives

### Primary Goals
1. Run full integration tests with real 3,830-card CSV dataset
2. Validate end-to-end import/export workflows
3. Verify Scryfall enrichment performance and reliability
4. Ensure database integrity and backup/restore functionality
5. Performance profiling and optimization
6. Final code review and documentation updates

### Success Metrics
- ✅ All integration tests passing
- ✅ 3,830-card import completes successfully
- ✅ Scryfall enrichment completes in <20 minutes
- ✅ No data loss or corruption
- ✅ Backup/restore procedures validated
- ✅ Export outputs verified across all 4 formats
- ✅ Error handling tested with edge cases
- ✅ Code coverage >80% for critical paths
- ✅ Documentation complete and accurate
- ✅ Phase 1 completion at 75%

---

## Testing Scope

### 1. Integration Tests Execution
**Module**: `tests/integration/test_import_workflow.py`

**Test Classes**:
- `TestCSVImporter`: All 4 format importers
- `TestBackupManager`: Backup creation/listing/restore
- `TestMigrationManager`: End-to-end import workflow
- `TestBatchInsertService`: Bulk insertion and deduplication
- `TestEndToEndWorkflow`: Complete import → enrichment → insert workflow

**Execution Plan**:
```bash
pytest tests/integration/test_import_workflow.py -v
pytest tests/integration/test_import_workflow.py::TestCSVImporter -v
pytest tests/integration/test_import_workflow.py::TestEndToEndWorkflow -v
```

**Expected Results**:
- 15+ tests passing
- All importers working correctly
- Backup/restore procedures validated
- Deduplication logic working
- Statistics tracking accurate

### 2. Real Data Testing
**Dataset**: `data/imports/ManaBox_Collection_Bulk.csv` (3,830 cards)

**Steps**:
1. Run import with auto-detect format
2. Monitor Scryfall enrichment progress
3. Validate card count matches CSV
4. Check for duplicate handling
5. Verify price data enrichment
6. Validate database structure

**Expected Results**:
- 3,830 cards imported successfully
- <10% Scryfall lookup failures (normal for older/custom cards)
- Enrichment completes in 10-15 minutes
- No duplicate items created
- Database integrity verified

### 3. Export Format Validation
**Formats to Test**: CSV, Moxfield, Archidekt, JSON

**Testing Procedure**:
1. Export to each format
2. Verify file structure
3. Spot-check card data accuracy
4. Test filtering options
5. Validate price inclusion

**Expected Results**:
- All 4 formats export successfully
- Card data matches source
- Filters work correctly
- File sizes reasonable
- No data corruption

### 4. Scryfall Integration Testing
**Aspects**:
- Rate limiting adherence
- Cache effectiveness
- Error handling for missing cards
- Price data accuracy
- Performance under load

**Testing**:
1. Monitor request patterns
2. Verify rate limit enforcement
3. Check cache hit rate
4. Test with edge cases (old sets, misprints)
5. Validate price update frequency

**Expected Results**:
- Rate limiting working (10 req/sec)
- Cache improves performance (>50% hit rate)
- Graceful handling of missing cards
- Accurate pricing data
- Consistent response times

### 5. Database Integrity Checks
**Validations**:
- No orphaned records
- Referential integrity
- Constraint enforcement
- Index effectiveness
- Query performance

**Testing**:
```python
# Check for orphaned collection items
orphaned = session.query(CollectionItem).filter(
    ~exists(select(1).where(Card.id == CollectionItem.card_id))
).count()

# Verify unique constraints
duplicates = session.query(Card).group_by(
    Card.scryfall_id
).having(count(Card.id) > 1).count()
```

**Expected Results**:
- Zero orphaned records
- Zero constraint violations
- Indexes working efficiently
- Query performance <100ms

### 6. Error Recovery Testing
**Scenarios**:
- Invalid CSV data
- Missing Scryfall matches
- Database connection errors
- Backup restoration
- Partial import failures

**Testing**:
1. Introduce test errors in CSV
2. Test with incomplete Scryfall data
3. Simulate connection issues
4. Validate error messages
5. Test recovery procedures

**Expected Results**:
- Graceful error handling
- Clear error messages
- Recovery procedures work
- No data loss on errors
- Informative logging

### 7. Performance Profiling
**Metrics to Measure**:
- CSV parsing time
- Scryfall API latency
- Database insertion rate
- Memory usage
- Cache effectiveness
- Total end-to-end time

**Tools**:
- Python `cProfile` for CPU profiling
- `memory_profiler` for memory usage
- Custom timing decorators
- asyncio task tracking

**Expected Results**:
- CSV parsing: <1 second
- Scryfall enrichment: 10-15 minutes (3,830 cards)
- Database insertion: 1-2 minutes
- Memory: <500MB peak
- Total: <20 minutes end-to-end

---

## Implementation Plan

### Phase 1: Test Infrastructure Setup (15 min)
- [ ] Create test data fixtures
- [ ] Set up test database isolation
- [ ] Configure logging for test runs
- [ ] Create performance tracking utilities

### Phase 2: Integration Tests Execution (30 min)
- [ ] Run unit tests for importers
- [ ] Run backup/restore tests
- [ ] Run migration manager tests
- [ ] Run end-to-end workflow tests
- [ ] Document test results

### Phase 3: Real Data Validation (25 min)
- [ ] Import 3,830-card CSV
- [ ] Monitor enrichment progress
- [ ] Validate card counts
- [ ] Verify pricing data
- [ ] Check database integrity

### Phase 4: Export Validation (15 min)
- [ ] Test CSV export
- [ ] Test Moxfield export
- [ ] Test Archidekt export
- [ ] Test JSON export
- [ ] Verify filtering options

### Phase 5: Performance Analysis (10 min)
- [ ] Run performance profiler
- [ ] Analyze bottlenecks
- [ ] Document metrics
- [ ] Suggest optimizations

### Phase 6: Final Cleanup (15 min)
- [ ] Code review and cleanup
- [ ] Update documentation
- [ ] Update progress tracker
- [ ] Final commit

---

## Detailed Test Cases

### CSV Importer Tests

**Test: ManaBox Format Detection**
```python
def test_manabox_format_auto_detection():
    csv_file = create_sample_csv("manabox")
    cards, errors = import_csv(csv_file)
    assert len(cards) >= 3
    assert len(errors) == 0
    assert all(c.name for c in cards)
    assert all(c.set_code for c in cards)
```

**Test: Flexible Header Matching**
```python
def test_flexible_headers():
    # Test with different column names
    csv_variations = [
        "Name,Set Code,Quantity",
        "Card Name,Set,Qty",
        "name,set code,quantity",
    ]
    for variation in csv_variations:
        cards, errors = import_csv(variation)
        assert len(cards) > 0
        assert len(errors) == 0
```

**Test: Error Line Tracking**
```python
def test_error_line_tracking():
    csv_file = create_csv_with_errors()
    cards, errors = import_csv(csv_file)
    assert len(errors) > 0
    for line_num, error_msg in errors:
        assert isinstance(line_num, int)
        assert isinstance(error_msg, str)
```

### Scryfall Integration Tests

**Test: Rate Limiting Enforcement**
```python
async def test_rate_limiting():
    client = ScryfallClient()
    start = time.time()
    
    for i in range(20):
        await client.search_card(f"Card{i}", "kmg")
    
    elapsed = time.time() - start
    # 20 requests at 10 req/sec should take ~2 seconds
    assert elapsed >= 2.0
```

**Test: Cache Effectiveness**
```python
async def test_cache_hits():
    client = ScryfallClient(cache_enabled=True)
    
    # First call: cache miss
    card1 = await client.search_card("Llanowar Elves", "rna")
    
    # Second call: cache hit
    card2 = await client.search_card("Llanowar Elves", "rna")
    
    assert card1 == card2
    assert client.cache is not None
    assert ("Llanowar Elves", "rna") in client.cache
```

**Test: Missing Card Handling**
```python
async def test_missing_card_handling():
    client = ScryfallClient()
    
    # Non-existent card
    card = await client.search_card("XYZ123NonExistent", "xyz")
    assert card is None
    
    # Should not raise exception
    assert True
```

### Batch Insert Tests

**Test: Deduplication Logic**
```python
def test_deduplication():
    cards = [
        CardImport("Llanowar Elves", "rna", quantity=2, is_foil=False),
        CardImport("Llanowar Elves", "rna", quantity=3, is_foil=False),
        CardImport("Llanowar Elves", "rna", quantity=1, is_foil=True),
    ]
    
    service = BatchInsertService(session)
    stats = service.insert_collection_items(cards)
    
    # Should create 2 collection items (1 non-foil, 1 foil)
    assert session.query(CollectionItem).count() == 2
    
    # Non-foil should have accumulated quantity
    non_foil = session.query(CollectionItem).filter(
        CollectionItem.is_foil == False
    ).first()
    assert non_foil.quantity == 5  # 2 + 3
```

**Test: Replace Mode**
```python
def test_replace_mode():
    # Create initial collection
    initial_cards = [CardImport("Card1", "set1", quantity=1)]
    service1 = BatchInsertService(session)
    service1.insert_collection_items(initial_cards)
    initial_count = session.query(CollectionItem).count()
    
    # Import with replace mode
    new_cards = [CardImport("Card2", "set2", quantity=1)]
    service2 = BatchInsertService(session)
    service2.insert_collection_items(new_cards, replace_mode=True)
    
    # Should have only new cards
    final_count = session.query(CollectionItem).count()
    assert final_count == 1
    assert session.query(CollectionItem).first().card.name == "Card2"
```

### End-to-End Workflow Tests

**Test: Complete Import Pipeline**
```python
async def test_complete_import_workflow():
    # 1. Import CSV
    csv_file = Path("data/imports/test_collection.csv")
    cards, errors = import_csv(csv_file)
    
    # 2. Enrich with Scryfall
    enrichment = EnrichmentService()
    scryfall_map, enrich_stats = await enrichment.enrich_imports(cards)
    
    # 3. Batch insert
    service = BatchInsertService(session)
    insert_stats = service.insert_collection_items(
        cards, scryfall_map=scryfall_map
    )
    
    # 4. Verify
    total_items = session.query(CollectionItem).count()
    assert total_items == len(set((c.name, c.set_code) for c in cards))
    
    # All stages should show success
    assert insert_stats["errors"] == 0 or insert_stats["errors"] < len(cards) / 10
    assert enrich_stats["errors"] < len(cards) / 10
```

---

## Documentation Updates

### Areas to Update:
1. **IMPORT_EXPORT_GUIDE.md**
   - Add real test results
   - Document expected timing
   - Add troubleshooting for common issues

2. **API Documentation**
   - Service method examples
   - Error handling patterns
   - Performance tips

3. **Development Guide**
   - Testing procedures
   - Performance profiling
   - Contributing guidelines

4. **README**
   - Project status (Phase 1: 75%)
   - Quick start guide
   - Features overview

---

## Success Criteria Checklist

### Testing
- [ ] All unit tests passing (50+)
- [ ] All integration tests passing (15+)
- [ ] Real 3,830-card import succeeding
- [ ] Export validation complete
- [ ] Performance profiling done
- [ ] Error recovery validated

### Code Quality
- [ ] Code review complete
- [ ] No critical issues found
- [ ] Type hints complete
- [ ] Docstrings present
- [ ] Comments clear

### Documentation
- [ ] IMPORT_EXPORT_GUIDE.md complete
- [ ] API documentation updated
- [ ] Examples provided
- [ ] Troubleshooting guide written

### Performance
- [ ] End-to-end time <20 minutes
- [ ] Memory usage <500MB peak
- [ ] Database queries optimized
- [ ] Cache effectiveness >50%

### Project Status
- [ ] Phase 1 at 75% completion
- [ ] Commits pushed to main
- [ ] Progress tracker updated
- [ ] Ready for Phase 2 (GUI)

---

## Exit Criteria

PROMPT 1.5 is complete when:
1. All integration tests pass
2. Real data import validated
3. Export formats verified
4. Performance acceptable
5. Documentation complete
6. Code cleanup done
7. Phase 1 reaches 75%
8. Ready for Phase 2 (GUI development)

---

## Post-PROMPT 1.5 State

### Deliverables:
- ✅ Complete testing infrastructure
- ✅ Validated import/export pipeline
- ✅ Performance benchmarks
- ✅ Comprehensive documentation
- ✅ Phase 1 at 75% completion (v0.75)

### Ready For:
- Phase 2: GUI Development (PyQt6)
- User beta testing
- Real-world collection imports
- Advanced analytics

### Known Limitations (Addressed in Phase 2+):
- No GUI interface (Phase 2)
- No real-time pricing (Phase 3)
- No sync features yet (Phase 3)
- No advanced analytics (Phase 3)

---

**Created**: During PROMPT 1.5 Execution
**Target Completion**: Current Session
**Estimated Duration**: 90 minutes
