import React, { useState, useEffect } from 'react';
import axios from 'axios';

function DeleteImage() {
    const [items, setItems] = useState([]);
    const [selectedItems, setSelectedItems] = useState(new Set());
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    // Fetch items when the component mounts
    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = async () => {
        try {
            setIsLoading(true);
            const response = await axios.get('http://127.0.0.1:5000/api/user-items');
            setItems(response.data);
            setError('');
        } catch (err) {
            setError('Failed to fetch items.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const toggleItemSelection = (itemId) => {
        const newSelection = new Set(selectedItems);
        if (newSelection.has(itemId)) {
            newSelection.delete(itemId);
        } else {
            newSelection.add(itemId);
        }
        setSelectedItems(newSelection);
    };

    const handleDelete = async () => {
        if (selectedItems.size === 0) {
            setError('Please select items to delete.');
            return;
        }

        setIsLoading(true);
        setError('');
        setMessage('');

        try {
            const response = await axios.post('http://127.0.0.1:5000/api/delete-items', {
                item_ids: Array.from(selectedItems),
            });
            setMessage(response.data.message);
            setSelectedItems(new Set()); // Clear selection
            fetchItems(); // Refresh the list of items
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred during deletion.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Delete Wardrobe Items</h2>
            <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                <p>Select one or more items to permanently delete them.</p>
                <button onClick={handleDelete} disabled={isLoading || selectedItems.size === 0}>
                    {isLoading ? 'Deleting...' : `Delete ${selectedItems.size} Selected Item(s)`}
                </button>
                {message && <p style={{ color: 'green', marginTop: '10px' }}>{message}</p>}
                {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
            </div>

            {isLoading && items.length === 0 ? <p>Loading items...</p> : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '10px' }}>
                    {items.map(item => (
                        <div 
                            key={item.id} 
                            onClick={() => toggleItemSelection(item.id)}
                            style={{ 
                                cursor: 'pointer', 
                                border: selectedItems.has(item.id) ? '3px solid dodgerblue' : '3px solid transparent',
                                borderRadius: '4px',
                                padding: '2px'
                            }}
                        >
                            <img src={item.url} alt={item.id} style={{ width: '100%', height: '150px', objectFit: 'cover' }} />
                            <p style={{ textAlign: 'center', margin: '5px 0 0 0' }}>ID: {item.id}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default DeleteImage;