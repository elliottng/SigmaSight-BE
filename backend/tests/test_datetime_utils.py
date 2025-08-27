"""
Comprehensive test suite for datetime_utils module.

Tests UTC ISO 8601 standardization functions for correctness,
edge cases, and compatibility scenarios.

Author: SigmaSight Team
Date: 2025-08-27
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from app.core.datetime_utils import (
    utc_now,
    utc_now_iso8601,
    to_utc_iso8601,
    to_iso_date,
    parse_iso8601,
    standardize_datetime_field,
    standardize_datetime_dict,
    standardize_datetime_list,
    is_datetime_field,
    validate_iso8601_format,
    ensure_utc_datetime
)


class TestBasicFunctions:
    """Test basic datetime utility functions."""
    
    def test_utc_now_returns_datetime(self):
        """Test that utc_now returns a datetime object."""
        result = utc_now()
        assert isinstance(result, datetime)
        assert result.tzinfo is None  # Should be naive
        
    def test_utc_now_iso8601_format(self):
        """Test that utc_now_iso8601 returns properly formatted string."""
        result = utc_now_iso8601()
        assert isinstance(result, str)
        assert result.endswith('Z')
        assert 'T' in result
        assert validate_iso8601_format(result)


class TestToUtcIso8601:
    """Test to_utc_iso8601 conversion function."""
    
    def test_none_returns_none(self):
        """Test that None input returns None."""
        assert to_utc_iso8601(None) is None
    
    def test_naive_datetime_assumes_utc(self):
        """Test that naive datetime is assumed to be UTC."""
        dt = datetime(2025, 8, 27, 10, 30, 45, 123456)
        result = to_utc_iso8601(dt)
        assert result == '2025-08-27T10:30:45.123456Z'
    
    def test_utc_timezone_aware(self):
        """Test timezone-aware UTC datetime."""
        dt = datetime(2025, 8, 27, 10, 30, 45, tzinfo=timezone.utc)
        result = to_utc_iso8601(dt)
        assert result == '2025-08-27T10:30:45Z'
    
    def test_other_timezone_converts_to_utc(self):
        """Test that non-UTC timezone is converted to UTC."""
        # Create a datetime in EST (UTC-5)
        est = timezone(timedelta(hours=-5))
        dt = datetime(2025, 8, 27, 10, 30, 45, tzinfo=est)
        result = to_utc_iso8601(dt)
        # Should be converted to UTC (15:30:45)
        assert result == '2025-08-27T15:30:45Z'
    
    def test_microseconds_preserved(self):
        """Test that microseconds are preserved in conversion."""
        dt = datetime(2025, 8, 27, 10, 30, 45, 987654)
        result = to_utc_iso8601(dt)
        assert '.987654' in result


class TestToIsoDate:
    """Test to_iso_date conversion function."""
    
    def test_none_returns_none(self):
        """Test that None input returns None."""
        assert to_iso_date(None) is None
    
    def test_date_formatting(self):
        """Test proper date formatting."""
        d = date(2025, 8, 27)
        result = to_iso_date(d)
        assert result == '2025-08-27'
    
    def test_datetime_date_component(self):
        """Test that we can convert datetime.date()."""
        dt = datetime(2025, 8, 27, 10, 30, 45)
        result = to_iso_date(dt.date())
        assert result == '2025-08-27'


class TestParseIso8601:
    """Test parse_iso8601 function."""
    
    def test_none_returns_none(self):
        """Test that None input returns None."""
        assert parse_iso8601(None) is None
    
    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        assert parse_iso8601('') is None
    
    def test_parse_with_z_suffix(self):
        """Test parsing ISO 8601 with Z suffix."""
        result = parse_iso8601('2025-08-27T10:30:45Z')
        assert result == datetime(2025, 8, 27, 10, 30, 45)
        assert result.tzinfo is None  # Should be naive
    
    def test_parse_with_timezone_offset(self):
        """Test parsing ISO 8601 with timezone offset."""
        result = parse_iso8601('2025-08-27T10:30:45+00:00')
        assert result == datetime(2025, 8, 27, 10, 30, 45)
        assert result.tzinfo is None
    
    def test_parse_with_non_utc_timezone(self):
        """Test parsing with non-UTC timezone (converts to UTC)."""
        # EST time (UTC-5)
        result = parse_iso8601('2025-08-27T10:30:45-05:00')
        # Should be converted to UTC (15:30:45)
        assert result == datetime(2025, 8, 27, 15, 30, 45)
        assert result.tzinfo is None
    
    def test_parse_naive_datetime(self):
        """Test parsing naive datetime string (assumes UTC)."""
        result = parse_iso8601('2025-08-27T10:30:45')
        assert result == datetime(2025, 8, 27, 10, 30, 45)
        assert result.tzinfo is None
    
    def test_parse_with_microseconds(self):
        """Test parsing with microseconds."""
        result = parse_iso8601('2025-08-27T10:30:45.123456Z')
        assert result == datetime(2025, 8, 27, 10, 30, 45, 123456)
    
    def test_parse_invalid_format_returns_none(self):
        """Test that invalid format returns None."""
        assert parse_iso8601('not-a-date') is None
        assert parse_iso8601('2025/08/27') is None


class TestStandardizeDatetimeField:
    """Test standardize_datetime_field function."""
    
    def test_datetime_conversion(self):
        """Test datetime object conversion."""
        dt = datetime(2025, 8, 27, 10, 30, 45)
        result = standardize_datetime_field(dt)
        assert result == '2025-08-27T10:30:45Z'
    
    def test_date_conversion(self):
        """Test date object conversion."""
        d = date(2025, 8, 27)
        result = standardize_datetime_field(d)
        assert result == '2025-08-27'
    
    def test_string_with_timezone_offset(self):
        """Test string with +00:00 is converted to Z."""
        value = '2025-08-27T10:30:45.123456+00:00'
        result = standardize_datetime_field(value)
        assert result == '2025-08-27T10:30:45.123456Z'
    
    def test_other_types_unchanged(self):
        """Test that other types are returned unchanged."""
        assert standardize_datetime_field(42) == 42
        assert standardize_datetime_field('regular string') == 'regular string'
        assert standardize_datetime_field(None) is None
        assert standardize_datetime_field([1, 2, 3]) == [1, 2, 3]


class TestStandardizeDatetimeDict:
    """Test standardize_datetime_dict function."""
    
    def test_simple_dict(self):
        """Test standardization of simple dictionary."""
        data = {
            'created_at': datetime(2025, 8, 27, 10, 30, 45),
            'date': date(2025, 8, 27),
            'name': 'test',
            'count': 42
        }
        result = standardize_datetime_dict(data)
        
        assert result['created_at'] == '2025-08-27T10:30:45Z'
        assert result['date'] == '2025-08-27'
        assert result['name'] == 'test'
        assert result['count'] == 42
    
    def test_nested_dict(self):
        """Test standardization of nested dictionary."""
        data = {
            'portfolio': {
                'created_at': datetime(2025, 8, 27, 10, 30, 45),
                'positions': {
                    'updated_at': datetime(2025, 8, 27, 11, 0, 0)
                }
            }
        }
        result = standardize_datetime_dict(data)
        
        assert result['portfolio']['created_at'] == '2025-08-27T10:30:45Z'
        assert result['portfolio']['positions']['updated_at'] == '2025-08-27T11:00:00Z'
    
    def test_dict_with_list(self):
        """Test dictionary containing lists."""
        data = {
            'items': [
                {'created_at': datetime(2025, 8, 27, 10, 30)},
                {'created_at': datetime(2025, 8, 27, 11, 30)}
            ]
        }
        result = standardize_datetime_dict(data)
        
        assert result['items'][0]['created_at'] == '2025-08-27T10:30:00Z'
        assert result['items'][1]['created_at'] == '2025-08-27T11:30:00Z'
    
    def test_depth_limit(self):
        """Test that depth limit prevents infinite recursion."""
        # Create deeply nested structure
        dt = datetime(2025, 8, 27, 10, 30, 45)
        data = {'level1': {'level2': {'level3': {'created_at': dt}}}}
        
        # With depth=1, only level1 is processed
        result = standardize_datetime_dict(data, depth=1)
        assert isinstance(result['level1'], dict)
        # level2 and beyond not processed
        assert result['level1']['level2']['level3']['created_at'] == dt
        
        # With depth=4, all levels should be processed
        result = standardize_datetime_dict(data, depth=4)
        assert result['level1']['level2']['level3']['created_at'] == '2025-08-27T10:30:45Z'


class TestStandardizeDatetimeList:
    """Test standardize_datetime_list function."""
    
    def test_list_of_dicts(self):
        """Test list containing dictionaries."""
        data = [
            {'created_at': datetime(2025, 8, 27, 10, 30)},
            {'created_at': datetime(2025, 8, 27, 11, 30)}
        ]
        result = standardize_datetime_list(data)
        
        assert result[0]['created_at'] == '2025-08-27T10:30:00Z'
        assert result[1]['created_at'] == '2025-08-27T11:30:00Z'
    
    def test_list_of_values(self):
        """Test list containing direct values."""
        data = [
            datetime(2025, 8, 27, 10, 30),
            date(2025, 8, 27),
            'string',
            42
        ]
        result = standardize_datetime_list(data)
        
        assert result[0] == '2025-08-27T10:30:00Z'
        assert result[1] == '2025-08-27'
        assert result[2] == 'string'
        assert result[3] == 42


class TestIsDatetimeField:
    """Test is_datetime_field function."""
    
    def test_common_datetime_fields(self):
        """Test detection of common datetime field names."""
        assert is_datetime_field('created_at') is True
        assert is_datetime_field('updated_at') is True
        assert is_datetime_field('deleted_at') is True
        assert is_datetime_field('timestamp') is True
        assert is_datetime_field('start_date') is True
        assert is_datetime_field('end_time') is True
        assert is_datetime_field('expiry') is True
        assert is_datetime_field('expiration_date') is True
    
    def test_non_datetime_fields(self):
        """Test that non-datetime fields return False."""
        assert is_datetime_field('name') is False
        assert is_datetime_field('count') is False
        assert is_datetime_field('id') is False
        assert is_datetime_field('value') is False
    
    def test_case_insensitive(self):
        """Test that detection is case-insensitive."""
        assert is_datetime_field('CREATED_AT') is True
        assert is_datetime_field('Updated_At') is True
        assert is_datetime_field('TimeStamp') is True


class TestValidateIso8601Format:
    """Test validate_iso8601_format function."""
    
    def test_valid_formats(self):
        """Test valid ISO 8601 formats with Z suffix."""
        assert validate_iso8601_format('2025-08-27T10:30:45Z') is True
        assert validate_iso8601_format('2025-08-27T10:30:45.123Z') is True
        assert validate_iso8601_format('2025-08-27T10:30:45.123456Z') is True
    
    def test_invalid_formats(self):
        """Test invalid formats return False."""
        assert validate_iso8601_format('2025-08-27T10:30:45+00:00') is False  # Wrong suffix
        assert validate_iso8601_format('2025-08-27T10:30:45') is False  # No suffix
        assert validate_iso8601_format('2025-08-27') is False  # Date only
        assert validate_iso8601_format('not-a-date') is False
        assert validate_iso8601_format('') is False


class TestEnsureUtcDatetime:
    """Test ensure_utc_datetime function."""
    
    def test_naive_datetime_unchanged(self):
        """Test that naive datetime is returned unchanged."""
        dt = datetime(2025, 8, 27, 10, 30, 45)
        result = ensure_utc_datetime(dt)
        assert result == dt
        assert result.tzinfo is None
    
    def test_utc_timezone_aware_made_naive(self):
        """Test that UTC timezone-aware is made naive."""
        dt = datetime(2025, 8, 27, 10, 30, 45, tzinfo=timezone.utc)
        result = ensure_utc_datetime(dt)
        assert result == datetime(2025, 8, 27, 10, 30, 45)
        assert result.tzinfo is None
    
    def test_other_timezone_converted(self):
        """Test that other timezones are converted to UTC."""
        est = timezone(timedelta(hours=-5))
        dt = datetime(2025, 8, 27, 10, 30, 45, tzinfo=est)
        result = ensure_utc_datetime(dt)
        assert result == datetime(2025, 8, 27, 15, 30, 45)  # Converted to UTC
        assert result.tzinfo is None


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_sqlalchemy_datetime_with_offset(self):
        """Test handling SQLAlchemy DateTime with +00:00 offset."""
        # Simulate SQLAlchemy response
        data = {
            'portfolio': {
                'id': 'uuid-123',
                'name': 'Test Portfolio',
                'created_at': '2025-08-27T07:48:00.498537+00:00',
                'updated_at': '2025-08-27T08:15:30.123456+00:00'
            }
        }
        
        result = standardize_datetime_dict(data)
        assert result['portfolio']['created_at'] == '2025-08-27T07:48:00.498537Z'
        assert result['portfolio']['updated_at'] == '2025-08-27T08:15:30.123456Z'
    
    def test_mixed_formats_in_response(self):
        """Test handling mixed datetime formats in API response."""
        data = {
            'timestamp': datetime.utcnow(),
            'date': date.today(),
            'string_with_offset': '2025-08-27T10:30:45+00:00',
            'already_correct': '2025-08-27T11:30:45Z',
            'positions': [
                {'entry_date': date(2025, 8, 1)},
                {'entry_date': date(2025, 8, 15)}
            ]
        }
        
        result = standardize_datetime_dict(data)
        
        # Check all formats are standardized
        assert validate_iso8601_format(result['timestamp'])
        assert result['date'] == date.today().isoformat()
        assert result['string_with_offset'] == '2025-08-27T10:30:45Z'
        assert result['already_correct'] == '2025-08-27T11:30:45Z'
        assert result['positions'][0]['entry_date'] == '2025-08-01'
        assert result['positions'][1]['entry_date'] == '2025-08-15'
    
    def test_batch_calculation_timestamps(self):
        """Test standardization of batch calculation results."""
        # Simulate batch calculation results
        data = {
            'portfolio_id': 'uuid-123',
            'calculations': {
                'greeks': {
                    'calculated_at': datetime.utcnow(),
                    'results': [
                        {'position_id': 'pos-1', 'updated_at': datetime.utcnow()}
                    ]
                },
                'factors': {
                    'calculation_date': date.today(),
                    'exposures': []
                }
            }
        }
        
        result = standardize_datetime_dict(data)
        
        # All timestamps should be ISO 8601 with Z
        assert validate_iso8601_format(result['calculations']['greeks']['calculated_at'])
        assert validate_iso8601_format(
            result['calculations']['greeks']['results'][0]['updated_at']
        )
        assert result['calculations']['factors']['calculation_date'] == date.today().isoformat()


# Performance tests (optional, for benchmarking)
class TestPerformance:
    """Performance tests for datetime utilities."""
    
    def test_large_dict_performance(self):
        """Test performance with large dictionary."""
        import time
        
        # Create large nested structure
        data = {
            f'item_{i}': {
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'details': {
                    'modified_at': datetime.utcnow(),
                    'dates': [date.today() for _ in range(10)]
                }
            }
            for i in range(100)
        }
        
        start_time = time.time()
        result = standardize_datetime_dict(data)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 100ms for 100 items)
        assert elapsed < 0.1
        
        # Verify all items were processed
        assert len(result) == 100
        for key in result:
            assert validate_iso8601_format(result[key]['created_at'])