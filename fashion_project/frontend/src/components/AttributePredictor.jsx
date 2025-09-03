import React, { useState } from 'react';
import axios from 'axios';

function AttributePredictor() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [attributes, setAttributes] = useState(null);
    const [error, setError] = useState('');

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
            setAttributes(null); // Reset attributes on new file selection
        }
    };

    const handlePredict = async () => {
        if (!selectedFile) {
            setError('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await axios.post('http://127.0.0.1:5000/api/predict', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setAttributes(response.data);
            setError('');
        } catch (err) {
            setError('Error predicting attributes. Please try again.');
            console.error(err);
        }
    };

    return (
        <div>
            <h2>Attribute Predictor</h2>
            <input type="file" onChange={handleFileChange} accept="image/*" />
            <button onClick={handlePredict} disabled={!selectedFile}>
                Predict Attributes
            </button>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {preview && (
                <div>
                    <h3>Image Preview</h3>
                    <img src={preview} alt="Selected" width="300" />
                </div>
            )}

            {attributes && (
                <div>
                    <h3>Predicted Attributes</h3>
                    <p><strong>Article Type:</strong> {attributes.articleType}</p>
                    <p><strong>Category:</strong> {attributes.category}</p>
                    <p><strong>Event:</strong> {attributes.event}</p>
                </div>
            )}
        </div>
    );
}

export default AttributePredictor;