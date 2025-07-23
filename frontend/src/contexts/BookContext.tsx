'use client';

import React, { createContext, useContext, useState } from 'react';

interface BookMetadata {
  pages?: number;
  file_size?: number;
  subject?: string;
  creator?: string;
  producer?: string;
  creation_date?: string;
  modification_date?: string;
}

interface Book {
  id: number;
  title: string;
  cover: string;
  author: string;
  metadata?: BookMetadata;
  selected_at?: string;
  text_length?: number;
  source?: string;
}

interface BookContextType {
  selectedBook: Book | null;
  setSelectedBook: (book: Book | null) => void;
  updateBookMetadata: (metadata: BookMetadata) => void;
}

const BookContext = createContext<BookContextType | undefined>(undefined);

export function BookProvider({ children }: { children: React.ReactNode }) {
  const [selectedBook, setSelectedBook] = useState<Book | null>(() => {
    // Initialize from localStorage if available
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('selectedBook');
      if (stored) {
        try {
          return JSON.parse(stored);
        } catch (error) {
          console.error('Error parsing stored book:', error);
        }
      }
    }
    return null;
  });

  const setSelectedBookWithPersistence = (book: Book | null) => {
    setSelectedBook(book);
    // Persist to localStorage
    if (typeof window !== 'undefined') {
      if (book) {
        localStorage.setItem('selectedBook', JSON.stringify(book));
      } else {
        localStorage.removeItem('selectedBook');
      }
    }
  };

  const updateBookMetadata = (metadata: BookMetadata) => {
    if (selectedBook) {
      const updatedBook = {
        ...selectedBook,
        metadata: { ...selectedBook.metadata, ...metadata },
        selected_at: new Date().toISOString()
      };
      setSelectedBookWithPersistence(updatedBook);
    }
  };

  return (
    <BookContext.Provider value={{ selectedBook, setSelectedBook: setSelectedBookWithPersistence, updateBookMetadata }}>
      {children}
    </BookContext.Provider>
  );
}

export function useBook() {
  const context = useContext(BookContext);
  if (context === undefined) {
    throw new Error('useBook must be used within a BookProvider');
  }
  return context;
}
