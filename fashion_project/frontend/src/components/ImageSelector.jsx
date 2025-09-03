import React, { useState } from 'react';
import axios from 'axios';

function ImageSelector() {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [previews, setPreviews] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleFileChange = (event) => {
        const files = Array.from(event.target.files);
        if (files.length > 0) {
            setSelectedFiles(files);
            
            const imagePreviews = files.map(file => URL.createObjectURL(file));
            setPreviews(imagePreviews);
            
            // Clear previous messages
            setMessage('');
            setError('');
        }
    };

    const handleUpload = async () => {
        if (selectedFiles.length === 0) {
            setError('Please select images to upload.');
            return;
        }

        setIsLoading(true);
        setMessage('');
        setError('');

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await axios.post('http://127.0.0.1:5000/api/upload-item', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setMessage(response.data.message);
            // Clear selection after successful upload
            setSelectedFiles([]);
            setPreviews([]);
        } catch (err) {
            setError(err.response?.data?.message || 'An error occurred during upload.');
            setMessage('');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Add New Wardrobe Items</h2>
            
            <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
                <p>Select one or more images to add to your collection.</p>
                <input type="file" onChange={handleFileChange} accept="image/*" multiple />
                <button onClick={handleUpload} disabled={isLoading || selectedFiles.length === 0} style={{ marginLeft: '10px' }}>
                    {isLoading ? 'Uploading...' : `Upload ${selectedFiles.length} Item(s)`}
                </button>
            </div>

            {message && <p style={{ color: 'green', marginTop: '15px' }}>{message}</p>}
            {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}

            {/* --- Image Preview Section --- */}
            {previews.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                    <h4>Selected Images Preview</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '10px' }}>
                        {previews.map((previewUrl, index) => (
                            <img 
                                key={index} 
                                src={previewUrl} 
                                alt={`preview ${index}`} 
                                style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '4px' }}
                            />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default ImageSelector;