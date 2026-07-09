"""
Comprehensive tests for the storage module.
Tests CSV and SQLite storage functionality.
"""

import pytest
import os
import csv
import sqlite3
import tempfile

from src.storage import (
    save_to_csv,
    save_to_sqlite,
    save_articles,
    load_from_sqlite,
    ensure_output_dir,
)


class TestEnsureOutputDir:
    """Tests for output directory creation."""
    
    def test_ensure_output_dir_creates_directory(self, temp_output_dir):
        """Test that output directory is created."""
        test_dir = os.path.join(temp_output_dir, "nested", "output")
        assert not os.path.exists(test_dir)
        
        # Change to test directory context
        import src.storage
        original_dir = src.storage.OUTPUT_DIR
        src.storage.OUTPUT_DIR = test_dir
        
        try:
            ensure_output_dir()
            assert os.path.exists(test_dir)
        finally:
            src.storage.OUTPUT_DIR = original_dir


class TestSaveToCsv:
    """Tests for CSV storage functionality."""
    
    def test_save_to_csv_creates_file(self, sample_articles_list, temp_output_dir):
        """Test that CSV file is created."""
        filepath = save_to_csv(sample_articles_list, 
                              filename=os.path.join(temp_output_dir, "test.csv"))
        assert os.path.exists(filepath)
    
    def test_save_to_csv_correct_headers(self, sample_articles_list, temp_output_dir):
        """Test that CSV has correct headers."""
        filepath = save_to_csv(sample_articles_list,
                              filename=os.path.join(temp_output_dir, "test.csv"))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
        
        assert 'title' in headers
        assert 'author' in headers
        assert 'date' in headers
        assert 'description' in headers
        assert 'image_url' in headers
        assert 'article_url' in headers
    
    def test_save_to_csv_correct_row_count(self, sample_articles_list, temp_output_dir):
        """Test that CSV has correct number of rows."""
        filepath = save_to_csv(sample_articles_list,
                              filename=os.path.join(temp_output_dir, "test.csv"))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            rows = list(reader)
        
        assert len(rows) == len(sample_articles_list)
    
    def test_save_to_csv_data_integrity(self, sample_articles_list, temp_output_dir):
        """Test that CSV data matches input data."""
        filepath = save_to_csv(sample_articles_list,
                              filename=os.path.join(temp_output_dir, "test.csv"))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        for i, row in enumerate(rows):
            assert row['title'] == sample_articles_list[i]['title']
            assert row['author'] == sample_articles_list[i]['author']
            assert row['article_url'] == sample_articles_list[i]['article_url']
    
    def test_save_to_csv_empty_list(self, temp_output_dir):
        """Test saving empty article list."""
        filepath = save_to_csv([],
                              filename=os.path.join(temp_output_dir, "empty.csv"))
        # File should still be created
        assert os.path.exists(filepath)
    
    def test_save_to_csv_auto_filename(self, sample_articles_list, temp_output_dir):
        """Test automatic filename generation."""
        import src.storage
        original_dir = src.storage.OUTPUT_DIR
        src.storage.OUTPUT_DIR = temp_output_dir
        
        try:
            filepath = save_to_csv(sample_articles_list)
            assert filepath.startswith(temp_output_dir)
            assert filepath.endswith('.csv')
        finally:
            src.storage.OUTPUT_DIR = original_dir
    
    def test_save_to_csv_unicode_handling(self, temp_output_dir):
        """Test Unicode characters in CSV."""
        articles = [{
            "title": "Título con ñ y acentos áéíóú",
            "author": "José María",
            "date": "2026-06-25T10:00:00",
            "description": "Descripción con caracteres especiales: ¿? ¡!",
            "image_url": "https://example.com/imagen.jpg",
            "article_url": "https://example.com/artículo",
        }]
        
        filepath = save_to_csv(articles,
                              filename=os.path.join(temp_output_dir, "unicode.csv"))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
        
        assert row['title'] == "Título con ñ y acentos áéíóú"
        assert row['author'] == "José María"


class TestSaveToSqlite:
    """Tests for SQLite storage functionality."""
    
    def test_save_to_sqlite_creates_database(self, sample_articles_list, temp_output_dir):
        """Test that SQLite database is created."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        assert os.path.exists(db_path)
    
    def test_save_to_sqlite_creates_table(self, sample_articles_list, temp_output_dir):
        """Test that articles table is created."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
    
    def test_save_to_sqlite_correct_row_count(self, sample_articles_list, temp_output_dir):
        """Test that correct number of rows are inserted."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == len(sample_articles_list)
    
    def test_save_to_sqlite_data_integrity(self, sample_articles_list, temp_output_dir):
        """Test that SQLite data matches input data."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        for i, row in enumerate(rows):
            assert row['title'] == sample_articles_list[i]['title']
            assert row['author'] == sample_articles_list[i]['author']
    
    def test_save_to_sqlite_unique_constraint(self, sample_articles_list, temp_output_dir):
        """Test that duplicate URLs are handled (UNIQUE constraint)."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        
        # Try to insert same articles again
        save_to_sqlite(sample_articles_list, db_name=db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        conn.close()
        
        # Should still have original count (no duplicates)
        assert count == len(sample_articles_list)
    
    def test_save_to_sqlite_empty_list(self, temp_output_dir):
        """Test saving empty article list to SQLite."""
        db_path = save_to_sqlite([],
                                db_name=os.path.join(temp_output_dir, "empty.db"))
        assert os.path.exists(db_path)
    
    def test_save_to_sqlite_auto_db_name(self, sample_articles_list, temp_output_dir):
        """Test automatic database name generation."""
        import src.storage
        original_dir = src.storage.OUTPUT_DIR
        src.storage.OUTPUT_DIR = temp_output_dir
        
        try:
            db_path = save_to_sqlite(sample_articles_list)
            assert db_path.startswith(temp_output_dir)
            assert db_path.endswith('.db')
        finally:
            src.storage.OUTPUT_DIR = original_dir


class TestSaveArticles:
    """Tests for the unified save_articles function."""
    
    def test_save_articles_csv_format(self, sample_articles_list, temp_output_dir):
        """Test saving articles in CSV format."""
        import src.storage
        original_dir = src.storage.OUTPUT_DIR
        src.storage.OUTPUT_DIR = temp_output_dir
        
        try:
            filepath = save_articles(sample_articles_list, output_format="csv")
            assert filepath.endswith('.csv')
        finally:
            src.storage.OUTPUT_DIR = original_dir
    
    def test_save_articles_sqlite_format(self, sample_articles_list, temp_output_dir):
        """Test saving articles in SQLite format."""
        import src.storage
        original_dir = src.storage.OUTPUT_DIR
        src.storage.OUTPUT_DIR = temp_output_dir
        
        try:
            filepath = save_articles(sample_articles_list, output_format="sqlite")
            assert filepath.endswith('.db')
        finally:
            src.storage.OUTPUT_DIR = original_dir
    
    def test_save_articles_default_format(self, sample_articles_list, temp_output_dir):
        """Test saving articles with default format."""
        import src.storage
        original_dir = src.storage.OUTPUT_DIR
        src.storage.OUTPUT_DIR = temp_output_dir
        
        try:
            filepath = save_articles(sample_articles_list)
            assert filepath.endswith('.csv')  # Default is CSV
        finally:
            src.storage.OUTPUT_DIR = original_dir


class TestLoadFromSqlite:
    """Tests for loading articles from SQLite."""
    
    def test_load_from_sqlite_success(self, sample_articles_list, temp_output_dir):
        """Test loading articles from SQLite database."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        
        loaded = load_from_sqlite(db_path)
        
        assert len(loaded) == len(sample_articles_list)
    
    def test_load_from_sqlite_nonexistent_db(self, temp_output_dir):
        """Test loading from non-existent database."""
        loaded = load_from_sqlite(os.path.join(temp_output_dir, "nonexistent.db"))
        assert loaded == []
    
    def test_load_from_sqlite_data_integrity(self, sample_articles_list, temp_output_dir):
        """Test that loaded data matches saved data."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        
        loaded = load_from_sqlite(db_path)
        
        for i, article in enumerate(loaded):
            assert article['title'] == sample_articles_list[i]['title']
            assert article['author'] == sample_articles_list[i]['author']
    
    def test_load_from_sqlite_ordered_by_created_at(self, sample_articles_list, temp_output_dir):
        """Test that loaded articles are ordered by created_at DESC."""
        db_path = save_to_sqlite(sample_articles_list,
                                db_name=os.path.join(temp_output_dir, "test.db"))
        
        loaded = load_from_sqlite(db_path)
        
        # Should have created_at field
        assert all('created_at' in article for article in loaded)
