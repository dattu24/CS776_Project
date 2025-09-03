import React, { useState } from 'react';
import axios from 'axios';

function OccasionOutfit() {
    const [description, setDescription] = useState('A casual day out with friends');
    const [generatedOutfit, setGeneratedOutfit] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleGenerate = async () => {
        if (!description.trim()) {
            setError('Please enter a description.');
            return;
        }

        setIsLoading(true);
        setError('');
        setGeneratedOutfit([]);

        try {
            const response = await axios.post('http://127.0.0.1:5000/api/generate-occasion-outfit', {
                description: description,
            });
            setGeneratedOutfit(response.data.outfit_images || []);
        } catch (err) {
            setError(err.response?.data?.error || 'An unexpected error occurred.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Occasion-Based Outfit Generator</h2>
            
            {/* --- Input Section --- */}
            <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
                <label htmlFor="occasion-desc">Enter a description (e.g., "wedding", "office party"):</label>
                <textarea
                    id="occasion-desc"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows="3"
                    style={{ width: '100%', marginTop: '5px', padding: '8px' }}
                />
                
                <button onClick={handleGenerate} disabled={isLoading} style={{ marginTop: '10px' }}>
                    {isLoading ? 'Generating...' : 'Generate Outfit'}
                </button>
            </div>

            {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}

            {/* --- Output Section --- */}
            {generatedOutfit.length > 0 && (
                <div style={{ marginTop: '30px' }}>
                    <h3>Generated Outfit</h3>
                    <div style={{ display: 'flex', gap: '15px', overflowX: 'auto', padding: '10px' }}>
                        {generatedOutfit.map((imgUrl, index) => (
                            <div key={index} style={{ textAlign: 'center' }}>
                                <img src={imgUrl} alt={`Outfit item ${index + 1}`} style={{ height: '200px', border: '1px solid #eee' }} />
                                <p style={{ fontSize: '12px' }}>{imgUrl.split('/').pop()}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default OccasionOutfit;