# 📚 Smart Glasses Documentation Index

**Complete guide to all documentation in this project**

---

## 🚀 Quick Start (New Users Start Here!)

1. **[README.md](README.md)** - Project overview and quick start
2. **[INSTALL.md](INSTALL.md)** - Installation instructions (Python, dependencies)
3. **[docs/QUICKREF.md](docs/QUICKREF.md)** - Quick command reference

**First-time setup**: `README.md` → `INSTALL.md` → `docs/QUICKREF.md` → `docs/USAGE_GUIDE.md`

---

## 📖 User Guides (How to Use the System)

### Core Usage
- **[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)** - Complete guide to using the system
  - Running with video files
  - Running with webcam
  - Understanding the UI
  - Voice commands

### Feature-Specific Guides
- **[docs/WEBCAM_GUIDE.md](docs/WEBCAM_GUIDE.md)** - Using your laptop camera
  - Webcam setup
  - Testing camera
  - Troubleshooting

- **[docs/ML_INTEGRATION_GUIDE.md](docs/ML_INTEGRATION_GUIDE.md)** - Integrating real ML detectors
  - YOLO installation
  - YOLO-World for custom objects
  - Alternative detectors (TFLite, OpenCV DNN)

- **[docs/YOLO_CLASSES.md](docs/YOLO_CLASSES.md)** - List of 80 COCO classes
  - All objects YOLO can detect
  - Common objects reference

### Voice Features
- **[docs/VOICE_GUIDE.md](docs/VOICE_GUIDE.md)** - Voice input and output overview
  - Voice commands
  - Speech recognition setup
  - Common issues

- **[docs/VOICE_OUTPUT_GUIDE.md](docs/VOICE_OUTPUT_GUIDE.md)** - Customizing voice output
  - Changing voice (male/female)
  - Adjusting speed and volume
  - Voice settings

- **[docs/SCENE_DESCRIPTION_EXPLAINED.md](docs/SCENE_DESCRIPTION_EXPLAINED.md)** - How scene description works
  - Technical details
  - Rule-based generation
  - No LLMs used

---

## 🏗️ Architecture & Design (For Developers)

### Primary Architecture Reference
- **[docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)** ⭐ **START HERE**
  - Complete system architecture (48K!)
  - 10 levels of detail (L0 to L9)
  - All modules explained
  - Data flow diagrams
  - Message contracts
  - Integration patterns

### Supporting Architecture Docs
- **[docs/COMPONENT_STATUS.md](docs/COMPONENT_STATUS.md)** - What's implemented vs future
  - Fully implemented components
  - Partially implemented components
  - Future/planned components
  - Responsibility matrix

- **[docs/DIAGRAM_LEGEND.md](docs/DIAGRAM_LEGEND.md)** - How to read architecture diagrams
  - Visual conventions
  - Color coding
  - Dotted boxes = future components
  - Solid boxes = implemented

- **[docs/message_contracts.md](docs/message_contracts.md)** - Detailed schema reference
  - All Pydantic models
  - Data contracts between modules

---

## 🔮 Future Design Documents (Upcoming Features)

### Map-Based Navigation
- **[docs/MAP_BASED_NAVIGATION.md](docs/MAP_BASED_NAVIGATION.md)** - Indoor navigation design
  - Requirements
  - Architecture
  - SLAM, localization, path planning
  - Implementation phases
  - **For navigation team reference**

### RFID Integration
- **[docs/RFID_INTEGRATION.md](docs/RFID_INTEGRATION.md)** - RFID detection design
  - RFID hardware integration
  - Sensor fusion module
  - Visual + RFID fusion
  - **For RFID team reference**

### Refactoring Plans
- **[docs/ARCHITECTURE_REFACTORING.md](docs/ARCHITECTURE_REFACTORING.md)** - Navigation → Spatial Analysis rename
  - Rationale for renaming
  - Migration plan
  - Breaking changes
  - **Note**: May be deleted after refactoring is complete

---

## 📋 Documentation by Audience

### 👤 End Users (Just Want to Use It)
```
1. README.md                   # What is this?
2. INSTALL.md                  # How to install?
3. docs/USAGE_GUIDE.md         # How to use?
4. docs/WEBCAM_GUIDE.md        # How to use my camera?
5. docs/VOICE_GUIDE.md         # How to use voice?
6. docs/QUICKREF.md            # Quick commands
```

### 👨‍💻 Developers (Want to Understand/Extend)
```
1. docs/SYSTEM_ARCHITECTURE.md      # How does it work?
2. docs/COMPONENT_STATUS.md         # What's implemented?
3. docs/DIAGRAM_LEGEND.md           # How to read diagrams?
4. docs/message_contracts.md        # What are the data contracts?
5. docs/ML_INTEGRATION_GUIDE.md     # How to add ML models?
```

### 🏢 Feature Teams (Navigation, RFID, etc.)
```
1. docs/SYSTEM_ARCHITECTURE.md      # Overall system
2. docs/MAP_BASED_NAVIGATION.md     # Navigation requirements
3. docs/RFID_INTEGRATION.md         # RFID requirements
4. docs/COMPONENT_STATUS.md         # Integration points
5. docs/ARCHITECTURE_REFACTORING.md # Ongoing changes
```

---

## 🗂️ Documentation by Topic

### Installation & Setup
- INSTALL.md
- README.md (Quick Start section)
- docs/QUICKREF.md

### Usage
- docs/USAGE_GUIDE.md
- docs/WEBCAM_GUIDE.md
- docs/VOICE_GUIDE.md
- docs/VOICE_OUTPUT_GUIDE.md
- docs/QUICKREF.md

### Architecture
- docs/SYSTEM_ARCHITECTURE.md ⭐
- docs/COMPONENT_STATUS.md
- docs/DIAGRAM_LEGEND.md
- docs/message_contracts.md

### Machine Learning
- docs/ML_INTEGRATION_GUIDE.md
- docs/YOLO_CLASSES.md

### Voice & Scene Description
- docs/VOICE_GUIDE.md
- docs/VOICE_OUTPUT_GUIDE.md
- docs/SCENE_DESCRIPTION_EXPLAINED.md

### Future Features
- docs/MAP_BASED_NAVIGATION.md
- docs/RFID_INTEGRATION.md
- docs/ARCHITECTURE_REFACTORING.md

---

## 🎯 Common Tasks → Documentation

| Task | Documentation |
|------|--------------|
| **First time setup** | README → INSTALL → docs/USAGE_GUIDE |
| **Run with webcam** | docs/WEBCAM_GUIDE |
| **Add voice commands** | docs/VOICE_GUIDE |
| **Customize voice output** | docs/VOICE_OUTPUT_GUIDE |
| **Integrate YOLO** | docs/ML_INTEGRATION_GUIDE |
| **Understand architecture** | docs/SYSTEM_ARCHITECTURE (start L0-L2) |
| **Find what's implemented** | docs/COMPONENT_STATUS |
| **Understand data flow** | docs/SYSTEM_ARCHITECTURE (L3-L5) |
| **Add new module** | docs/SYSTEM_ARCHITECTURE (L6-L8) |
| **Plan navigation feature** | docs/MAP_BASED_NAVIGATION |
| **Plan RFID feature** | docs/RFID_INTEGRATION |

---

## 📁 Directory Structure

```
smart-glasses/
├── README.md                           # ⭐ Start here
├── DOCS_INDEX.md                       # 📚 This file
├── INSTALL.md                          # Installation
│
└── docs/
    ├── README.md                       # Docs directory index
    ├── message_contracts.md            # Schema reference
    │
    ├── USAGE_GUIDE.md                  # User guides
    ├── QUICKREF.md
    ├── WEBCAM_GUIDE.md
    ├── ML_INTEGRATION_GUIDE.md
    ├── VOICE_GUIDE.md
    ├── VOICE_OUTPUT_GUIDE.md
    ├── SCENE_DESCRIPTION_EXPLAINED.md
    │
    ├── SYSTEM_ARCHITECTURE.md          # Architecture
    ├── COMPONENT_STATUS.md
    ├── DIAGRAM_LEGEND.md
    ├── YOLO_CLASSES.md
    │
    ├── MAP_BASED_NAVIGATION.md         # Future/planning
    ├── RFID_INTEGRATION.md
    ├── ARCHITECTURE_REFACTORING.md
    └── CLEANUP_PLAN.md
```

---

## 🔍 Finding Information

### "How do I...?"
→ **docs/USAGE_GUIDE.md** or specific feature guide (docs/WEBCAM_GUIDE, docs/VOICE_GUIDE, etc.)

### "What does...?"
→ **docs/SYSTEM_ARCHITECTURE.md** (search for module/component name)

### "How does X work?"
→ **docs/SYSTEM_ARCHITECTURE.md** (see relevant level L0-L9)

### "What can I detect?"
→ **docs/YOLO_CLASSES.md**

### "What's implemented?"
→ **docs/COMPONENT_STATUS.md**

### "What's planned for the future?"
→ **docs/MAP_BASED_NAVIGATION.md** or **docs/RFID_INTEGRATION.md**

---

## 💡 Documentation Best Practices

### For Readers
1. **Start with README** if you're new
2. **Jump to docs/SYSTEM_ARCHITECTURE** if you're technical
3. **Use this index** to find specific topics
4. **Check docs/COMPONENT_STATUS** to see what's real vs planned

### For Contributors
1. **Update docs/SYSTEM_ARCHITECTURE.md** for architectural changes
2. **Update docs/COMPONENT_STATUS.md** when completing features
3. **Keep guides in sync** with code changes
4. **Use dotted boxes** in diagrams for future components

---

## 📊 Documentation Statistics

| Category | Files | Total Size |
|----------|-------|------------|
| Getting Started | 3 | ~22K |
| User Guides | 7 | ~36K |
| Architecture | 4 | ~71K |
| Future Design | 3 | ~56K |
| **Total** | **17** | **~185K** |

---

## 🗑️ Archived Documentation

Historical documentation moved to `.archive_docs/`:
- Bug fix logs (resolved issues)
- Superseded architecture docs
- Old status files

These are kept for reference but not actively maintained.

---

## ❓ Still Can't Find What You Need?

1. Search docs/SYSTEM_ARCHITECTURE.md (it's comprehensive!)
2. Check docs/COMPONENT_STATUS.md (see what exists)
3. Look in code comments (modules are well-documented)
4. Ask the team!

---

**Last updated**: December 27, 2025  
**Total documentation**: 17 files in `/docs`, ~185K  
**Primary reference**: docs/SYSTEM_ARCHITECTURE.md (48K)  
**Root files**: 3 (README, DOCS_INDEX, INSTALL)

