import React, { useState } from 'react';
import axios from 'axios';

// The list of subcategories from your Tkinter app
const SUBCATEGORIES = [
    "Blazers", "Casualshoes", "Flipflops", "formalshoes", "heels", "jackets",
    "jeans", "Kurtas", "Kurtis", "NehruJackets", "nightsuits", "rainjackets",
    "sandals", "shirts", "shorts", "sportssandals", "sportsshoes", "sweaters",
    "sweatshirts", "trackpants", "tracksuits", "Trousers", "Tshirts", "WaaistCoat", "FlipFlops",
];

function OutfitGenerator() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [categories, setCategories] = useState(["", "", "", ""]);
    const [generatedOutfit, setGeneratedOutfit] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
            setGeneratedOutfit([]); // Reset output
            setError('');
        }
    };

    const handleCategoryChange = (index, value) => {
        const newCategories = [...categories];
        newCategories[index] = value;
        setCategories(newCategories);
    };

    const handleGenerate = async () => {
        if (!selectedFile) {
            setError('Please select a base image first.');
            return;
        }

        setIsLoading(true);
        setError('');

        const startItemId = selectedFile.name.replace(/\.[^/.]+$/, ""); // Get filename without extension
        const targetDescriptions = categories.filter(cat => cat !== ""); // Get non-empty categories

        try {
            const response = await axios.post('http://127.0.0.1:5000/api/generate-outfit', {
                start_item_id: startItemId,
                target_descriptions: targetDescriptions,
            });
            setGeneratedOutfit(response.data.outfit_images || []);
        } catch (err) {
            setError('Error generating outfit. Check the console for details.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Full Outfit Generator</h2>
            
            {/* --- Input Section --- */}
            <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
                <input type="file" onChange={handleFileChange} accept="image/*" />
                {preview && <img src={preview} alt="Base item" style={{ maxWidth: '250px', marginTop: '10px' }} />}
                
                <h4 style={{ marginTop: '20px' }}>Select Categories to Add (Optional)</h4>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    {[0, 1, 2, 3].map(i => (
                        <select key={i} value={categories[i]} onChange={(e) => handleCategoryChange(i, e.target.value)}>
                            <option value="">Category {i + 1}</option>
                            {SUBCATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                        </select>
                    ))}
                </div>
                
                <button onClick={handleGenerate} disabled={isLoading} style={{ marginTop: '20px' }}>
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

export default OutfitGenerator;