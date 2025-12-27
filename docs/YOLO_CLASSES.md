# YOLO Object Classes (COCO Dataset)

YOLOv8 is trained on the **COCO dataset** with **80 object classes**.

## ❌ NOT Supported (Your Questions):
- **Keys** ❌ - Not in COCO dataset
- **Chargers** ❌ - Not in COCO dataset
- **Cables/Wires** ❌ - Not in COCO dataset
- **Glasses (eyewear)** ❌ - Not in COCO dataset
- **Wallet** ❌ - Not in COCO dataset
- **Pen/Pencil** ❌ - Not in COCO dataset

## ✅ All 80 Supported Classes:

### People & Animals (17 classes)
1. **person** ✅
2. bird
3. cat
4. dog
5. horse
6. sheep
7. cow
8. elephant
9. bear
10. zebra
11. giraffe

### Vehicles (8 classes)
12. bicycle
13. car
14. motorcycle
15. airplane
16. bus
17. train
18. truck
19. boat

### Outdoor Objects (5 classes)
20. traffic light
21. fire hydrant
22. stop sign
23. parking meter
24. bench

### Accessories & Sports (16 classes)
25. backpack
26. umbrella
27. handbag
28. tie
29. suitcase
30. frisbee
31. skis
32. snowboard
33. sports ball
34. kite
35. baseball bat
36. baseball glove
37. skateboard
38. surfboard
39. tennis racket

### Kitchen & Food (24 classes)
40. bottle
41. wine glass
42. cup ✅
43. fork
44. knife
45. spoon
46. bowl
47. banana
48. apple
49. sandwich
50. orange
51. broccoli
52. carrot
53. hot dog
54. pizza
55. donut
56. cake

### Furniture & Home (11 classes)
57. chair ✅
58. couch
59. potted plant
60. bed
61. dining table
62. toilet

### Electronics (10 classes)
63. tv
64. laptop ✅
65. mouse ✅ (computer mouse)
66. remote ✅
67. keyboard ✅
68. cell phone ✅
69. microwave
70. oven
71. toaster
72. sink
73. refrigerator

### Other Household Items (7 classes)
74. book ✅
75. clock ✅
76. vase
77. scissors ✅
78. teddy bear
79. hair drier
80. toothbrush

---

## What This Means for Your Use Case:

### ✅ Will Detect:
- **Electronics**: laptop, cell phone, keyboard, mouse, remote, tv
- **Furniture**: chair, couch, bed, table
- **Kitchen items**: cup, bottle, bowl, microwave, oven, refrigerator
- **Common objects**: book, clock, scissors, backpack, umbrella
- **People and pets**: person, cat, dog

### ❌ Won't Detect (Not in COCO):
- **Small accessories**: keys, chargers, cables, pens, glasses
- **Documents**: papers, cards, ID
- **Office items**: stapler, tape, folders
- **Tools**: screwdriver, hammer (unless looks like sports equipment)

---

## Workarounds for Unsupported Objects:

### Option 1: Use a Different Model
- **YOLOv8-World**: Can detect ANY object with text prompts
- **OWL-ViT**: Open-vocabulary detection
- **CLIP + Detection**: Custom object detection

### Option 2: Train Custom YOLO Model
Add your own classes (keys, chargers, etc.):
```bash
# Train on custom dataset
yolo detect train data=custom_data.yaml model=yolov8n.pt epochs=100
```

### Option 3: Object Detection + Classification
1. Detect "handbag" or generic object
2. Use image classification on cropped region
3. Classify as "keys", "charger", etc.

### Option 4: Fine-tune on Edge Cases
Use **few-shot learning** to add new classes with minimal data.

---

## Testing Detection on Your Webcam:

Based on what YOLO can detect, try showing:

**Electronics (High Success Rate):**
- ✅ Cell phone (you already saw this!)
- ✅ Laptop
- ✅ Keyboard
- ✅ Mouse
- ✅ Remote control
- ✅ TV

**Furniture:**
- ✅ Chair (you already saw this!)
- ✅ Couch
- ✅ Bed
- ✅ Table

**Kitchen:**
- ✅ Cup/Mug
- ✅ Bottle
- ✅ Bowl
- ✅ Microwave

**Other:**
- ✅ Book
- ✅ Clock
- ✅ Backpack
- ✅ Umbrella
- ✅ Scissors

**Won't Work:**
- ❌ Keys (too small + not in COCO)
- ❌ Chargers (not in COCO)
- ❌ Cables (not in COCO)
- ❌ Glasses (eyewear, not in COCO)

---

## Why Keys & Chargers Aren't Detected:

1. **Not in training data**: COCO dataset focuses on common large objects
2. **Too small**: Most small objects (<5% of image) are hard to detect
3. **Generic appearance**: Keys/chargers vary too much in shape

---

## Alternative: Use YOLOv8-World (Open Vocabulary)

Install with:
```bash
pip install ultralytics
```

Use in code:
```python
from ultralytics import YOLOWorld

# Can detect ANY object you describe!
model = YOLOWorld("yolov8s-world.pt")
model.set_classes(["keys", "charger", "cable", "wallet", "glasses"])
results = model(image)
```

This uses **CLIP embeddings** to detect objects not in COCO!

---

## Summary:

| Object | Supported? | Notes |
|--------|-----------|-------|
| Keys | ❌ | Not in COCO, too small |
| Chargers | ❌ | Not in COCO |
| Cell Phone | ✅ | Works great! |
| Laptop | ✅ | Works great! |
| Cup | ✅ | Works great! |
| Book | ✅ | Works well |
| Chair | ✅ | Works great! |
| Mouse | ✅ | Computer mouse |
| Remote | ✅ | TV remote |
| Scissors | ✅ | Works if visible |

For keys and chargers, you'd need to either:
1. Use **YOLOv8-World** (open vocabulary)
2. Train a **custom model**
3. Use a different dataset (OpenImages has more classes)

---

Want me to help you set up YOLOv8-World for detecting keys and chargers?

