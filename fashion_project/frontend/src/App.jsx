import React, { useState } from "react";
import AttributePredictor from "./components/AttributePredictor";
import OutfitGenerator from "./components/OutfitGenerator";
import OccasionOutfit from "./components/OccasionOutfit";
import ImageSelector from "./components/ImageSelector";
import DeleteImage from "./components/DeleteImage";
import "./App.css"; // For basic styling

function App() {
  const [activeTab, setActiveTab] = useState("imageSelector");

  const renderActiveTab = () => {
    switch (activeTab) {
      case "imageSelector":
        return <ImageSelector />;
      case "predictor":
        return <AttributePredictor />;
      case "outfitGenerator":
        return <OutfitGenerator />;
      case "occasionOutfit":
        return <OccasionOutfit />;
      case "deleteImage":
        return <DeleteImage />;
      default:
        return <OccasionOutfit />;
    }
  };

  return (
    <div className="App">
      <nav>
        <button onClick={() => setActiveTab("imageSelector")}>
          Add New Item
        </button>
        <button onClick={() => setActiveTab("predictor")}>
          Attribute Predictor
        </button>
        <button onClick={() => setActiveTab("outfitGenerator")}>
          Full Outfit Generator
        </button>
        <button onClick={() => setActiveTab("occasionOutfit")}>
          Occasion Outfit
        </button>
        <button onClick={() => setActiveTab("deleteImage")}>
          Delete Items
        </button>
      </nav>
      <main>{renderActiveTab()}</main>
    </div>
  );
}

export default App;
