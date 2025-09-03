# Fashion Transformer: Occasion-Aware Outfit Recommendation

**Team: CVision Coders**

---

## 🎯 Problem Statement  
Selecting a cohesive, occasion-appropriate outfit from one’s personal wardrobe is time-consuming and stressful. This project develops **Fashion Transformer**, an end-to-end deep learning system that (1) classifies a user’s garment images, (2) detects the desired occasion, (3) uses predefined category templates per occasion, and (4) composes a complete, compatible outfit via a multi-head Transformer operating on enriched FashionCLIP embeddings.

---

## 📂 System Components  
1. **Wardrobe Classifier**  
   - Inputs: User’s garment images  
   - Method: CLIP features + MLP with SMOTE balancing  
   - Outputs: Category labels (e.g., Topwear, Footwear), attributes (color, usage, season)

2. **Occasion Detection**  
   - Inputs: Text query (e.g., “I have an interview”)  
   - Method: Rule-based matching against predefined occasion list  
   - Outputs: Occasion label (e.g., Interview, Party)

3. **Outfit Category Templates**  
   - Predefined item sequences per occasion (e.g., {Topwear, Bottomwear, Footwear} for Interview)  
   - Guides which garment types to select  

4. **Fashion Transformer**  
   - Inputs: FashionCLIP image & text embeddings + learnable category tokens  
   - Architecture: 6-layer, 16-head Transformer with style-subspace projections  
   - Outputs:  
     - Compatibility score (binary) via special token + FFN  
     - Complementary-item embedding for retrieval  

---

## 📊 Key Results  

| Task                              | Metric           | Non-Disjoint | Disjoint   |
|-----------------------------------|------------------|--------------|------------|
| **Compatibility Prediction**      | Accuracy / AUC   | 83.99% / 0.95| 82.26% / 0.92 |
| **Fill-In-Blank Retrieval (FITB)**| Top-1 Accuracy   | 69.36%       | 68.28%     |

- Outperforms prior Outfit Transformer (AUC 0.93, FITB ~67%) and CSA-Net (FITB 61.7%).  
- High recall (~0.93) indicates few false negatives in compatibility.

---

## 🛠️ Implementation  

- **Framework**: PyTorch, HuggingFace Transformers  
- **Pretrained Models**: FashionCLIP for multi-modal embeddings  
- **Training**:  
  - Optimizer: AdamW + OneCycleLR  
  - Mixed Precision (AMP)  
  - EarlyStopping on validation loss  
- **Inference Pipeline**:  
  1. Classify wardrobe items → embeddings + category tokens  
  2. Map text to occasion → select template  
  3. Greedy retrieval: sequentially retrieve each category item via Transformer  
  4. Output compatible full outfit  

---

## 🎓 Contributions  

1. **Category-Aware Tokens**: Inject garment-type context into Transformer  
2. **Style Subspace Projections**: Specialized attention heads for color, formality, pattern  
3. **Greedy Retrieval Heuristic**: Efficient sequential outfit generation  
4. **Multi-Task Transformer**: Joint compatibility scoring and complementary retrieval  

---

## 🔗 Resources  


- **Polyvore Compatibility Dataset**  
 

---


