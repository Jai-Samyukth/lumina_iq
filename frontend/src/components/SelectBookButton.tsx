'use client';

import { useState } from 'react';
import { Plus, Search, Book, X } from 'lucide-react';
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/react';
import { useBook } from '@/contexts/BookContext';

// Mock book data - in a real app, this would come from an API
const mockBooks = [
  {
    id: 1,
    title: "Ikigai - The Japanese secret to a long and happy life",
    cover: "/book-covers/ikigai.jpg",
    author: "Héctor García & Francesc Miralles"
  },
  {
    id: 2,
    title: "JavaScript Guide",
    cover: "/book-covers/javascript.jpg",
    author: "Various Authors"
  },
  {
    id: 3,
    title: "Python Basics",
    cover: "/book-covers/python.jpg",
    author: "Programming Team"
  },
  {
    id: 4,
    title: "Sample Book",
    cover: "/book-covers/sample.jpg",
    author: "Sample Author"
  }
];

export default function SelectBookButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { selectedBook, setSelectedBook } = useBook();

  const filteredBooks = mockBooks.filter(book =>
    book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    book.author.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelectBook = async (book: typeof mockBooks[0]) => {
    try {
      // Call the backend API to select and cache the book
      const response = await fetch('http://localhost:8000/api/books/select', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          title: book.title,
          author: book.author
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Book selected and cached:', result);

        // Update the frontend context with enhanced book information
        const enhancedBook = {
          ...book,
          metadata: result.metadata || {
            pages: result.metadata?.pages || 10,
            file_size: result.metadata?.file_size || 0,
            subject: result.metadata?.subject || 'General',
            creator: result.metadata?.creator || 'LuminaIQ-AI',
            producer: result.metadata?.producer || 'Book Service'
          },
          selected_at: result.cached_at || new Date().toISOString(),
          text_length: result.text_length || 0,
          source: 'book_selection'
        };

        setSelectedBook(enhancedBook);
        setIsOpen(false);

        // Show success message
        alert(`Book "${book.title}" selected successfully! Text has been cached for AI interactions.`);
      } else {
        const error = await response.json();
        console.error('Failed to select book:', error);
        alert(`Failed to select book: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error selecting book:', error);
      alert('Failed to select book. Please try again.');
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-primary hover:bg-primary/90 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 z-50 group floating-button"
        aria-label="Select Book"
      >
        <div className="flex items-center space-x-2">
          <Plus className="h-6 w-6" />
          <span className="hidden group-hover:block text-sm font-medium whitespace-nowrap">
            Select Book
          </span>
        </div>
      </button>

      {/* Modal */}
      <Dialog open={isOpen} onClose={setIsOpen} className="relative z-50">
        <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" />
        
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel className="bg-card-bg rounded-2xl shadow-2xl w-full max-w-4xl max-h-[80vh] overflow-hidden border border-border">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <DialogTitle className="text-2xl font-bold text-text font-display">
                Select a Book
              </DialogTitle>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-sidebar-bg rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-text-secondary" />
              </button>
            </div>

            {/* Search Bar */}
            <div className="p-6 border-b border-border">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-text-secondary" />
                <input
                  type="text"
                  placeholder="Search books by title or author..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-colors bg-background text-text placeholder-text-secondary"
                />
              </div>
            </div>

            {/* Book List */}
            <div className="p-6 overflow-y-auto max-h-96">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredBooks.map((book) => (
                  <div
                    key={book.id}
                    onClick={() => handleSelectBook(book)}
                    className="bg-sidebar-bg p-4 rounded-xl border border-border hover:border-primary cursor-pointer transition-all duration-200 hover:shadow-md group"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="bg-primary/10 p-3 rounded-lg group-hover:bg-primary/20 transition-colors">
                        <Book className="h-8 w-8 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-text text-sm mb-1 line-clamp-2">
                          {book.title}
                        </h3>
                        <p className="text-text-secondary text-xs">
                          {book.author}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {filteredBooks.length === 0 && (
                <div className="text-center py-12">
                  <Book className="h-12 w-12 text-text-secondary mx-auto mb-4" />
                  <p className="text-text-secondary">No books found matching your search.</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-border bg-sidebar-bg">
              <div className="flex justify-between items-center">
                <p className="text-sm text-text-secondary">
                  {filteredBooks.length} book{filteredBooks.length !== 1 ? 's' : ''} available
                </p>
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </DialogPanel>
        </div>
      </Dialog>
    </>
  );
}
