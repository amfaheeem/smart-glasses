# 📚 Documentation Directory

This directory contains all detailed technical documentation, guides, and design documents for the Smart Glasses project.

---

## 📂 Files in this Directory (17 total)

### 📖 User Guides (7 files)
- **USAGE_GUIDE.md** - Complete guide to using the system
- **QUICKREF.md** - Quick command reference
- **WEBCAM_GUIDE.md** - Using your laptop camera
- **ML_INTEGRATION_GUIDE.md** - Integrating real ML detectors (YOLO, etc.)
- **YOLO_CLASSES.md** - List of 80 COCO classes YOLO can detect
- **VOICE_GUIDE.md** - Voice input and output overview
- **VOICE_OUTPUT_GUIDE.md** - Customizing voice settings
- **SCENE_DESCRIPTION_EXPLAINED.md** - How scene description works

### 🏗️ Architecture & Design (4 files)
- **SYSTEM_ARCHITECTURE.md** ⭐ - Complete system architecture (48K!)
  - 10 levels of detail (L0 to L9)
  - All modules explained
  - Data flow diagrams
  - Message contracts
  - Integration patterns
- **COMPONENT_STATUS.md** - Implementation status (what's built vs planned)
- **DIAGRAM_LEGEND.md** - How to read architecture diagrams
- **message_contracts.md** - Detailed Pydantic schema reference

### 🔮 Future Design Documents (3 files)
- **MAP_BASED_NAVIGATION.md** - Indoor navigation design (for navigation team)
- **RFID_INTEGRATION.md** - RFID detection design (for RFID team)
- **ARCHITECTURE_REFACTORING.md** - Navigation → Spatial Analysis refactoring plan

### 🗂️ Planning & Archive (1 file)
- **CLEANUP_PLAN.md** - Documentation cleanup analysis

---

## 🎯 Quick Navigation

**Looking for...** | **See...**
--- | ---
How to use the system | [USAGE_GUIDE.md](USAGE_GUIDE.md)
Quick commands | [QUICKREF.md](QUICKREF.md)
Webcam setup | [WEBCAM_GUIDE.md](WEBCAM_GUIDE.md)
ML/YOLO integration | [ML_INTEGRATION_GUIDE.md](ML_INTEGRATION_GUIDE.md)
Voice features | [VOICE_GUIDE.md](VOICE_GUIDE.md)
System architecture | [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) ⭐
What's implemented | [COMPONENT_STATUS.md](COMPONENT_STATUS.md)
Data contracts | [message_contracts.md](message_contracts.md)
Future: Navigation | [MAP_BASED_NAVIGATION.md](MAP_BASED_NAVIGATION.md)
Future: RFID | [RFID_INTEGRATION.md](RFID_INTEGRATION.md)

---

## 🚀 Getting Started

### For New Users
1. Start with [../README.md](../README.md) in the root directory
2. Follow installation: [../INSTALL.md](../INSTALL.md)
3. Learn how to use: [USAGE_GUIDE.md](USAGE_GUIDE.md)

### For Developers
1. Read architecture: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) (start L0-L2)
2. Check implementation status: [COMPONENT_STATUS.md](COMPONENT_STATUS.md)
3. Understand data contracts: [message_contracts.md](message_contracts.md)

### For Feature Teams
1. Overall system: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
2. Navigation design: [MAP_BASED_NAVIGATION.md](MAP_BASED_NAVIGATION.md)
3. RFID design: [RFID_INTEGRATION.md](RFID_INTEGRATION.md)

---

## 📋 Root Directory Files (3 files)

The project root contains only essential entry-point documentation:
- **[../README.md](../README.md)** - Project overview and quick start
- **[../DOCS_INDEX.md](../DOCS_INDEX.md)** - Complete documentation index with organized navigation
- **[../INSTALL.md](../INSTALL.md)** - Installation instructions

**💡 Tip**: Use [../DOCS_INDEX.md](../DOCS_INDEX.md) to navigate all documentation by audience, topic, or task.

---

## 📁 Directory Structure

```
smart-glasses/
├── README.md              # ⭐ Project entry point
├── DOCS_INDEX.md          # 📚 Documentation hub
├── INSTALL.md             # 🚀 Installation
│
└── docs/                  # 📂 All detailed documentation
    ├── README.md          # This file
    │
    ├── USAGE_GUIDE.md     # User guides (7 files)
    ├── QUICKREF.md
    ├── WEBCAM_GUIDE.md
    ├── ML_INTEGRATION_GUIDE.md
    ├── YOLO_CLASSES.md
    ├── VOICE_GUIDE.md
    ├── VOICE_OUTPUT_GUIDE.md
    ├── SCENE_DESCRIPTION_EXPLAINED.md
    │
    ├── SYSTEM_ARCHITECTURE.md    # Architecture (4 files)
    ├── COMPONENT_STATUS.md
    ├── DIAGRAM_LEGEND.md
    ├── message_contracts.md
    │
    ├── MAP_BASED_NAVIGATION.md   # Future design (3 files)
    ├── RFID_INTEGRATION.md
    ├── ARCHITECTURE_REFACTORING.md
    │
    └── CLEANUP_PLAN.md           # Planning (1 file)
```

---

## 🔍 Documentation by Audience

### 👤 End Users (Want to Use It)
- [USAGE_GUIDE.md](USAGE_GUIDE.md)
- [QUICKREF.md](QUICKREF.md)
- [WEBCAM_GUIDE.md](WEBCAM_GUIDE.md)
- [VOICE_GUIDE.md](VOICE_GUIDE.md)
- [VOICE_OUTPUT_GUIDE.md](VOICE_OUTPUT_GUIDE.md)

### 👨‍💻 Developers (Want to Understand/Extend)
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) ⭐
- [COMPONENT_STATUS.md](COMPONENT_STATUS.md)
- [DIAGRAM_LEGEND.md](DIAGRAM_LEGEND.md)
- [message_contracts.md](message_contracts.md)
- [ML_INTEGRATION_GUIDE.md](ML_INTEGRATION_GUIDE.md)

### 🏢 Feature Teams (Navigation, RFID, etc.)
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- [MAP_BASED_NAVIGATION.md](MAP_BASED_NAVIGATION.md)
- [RFID_INTEGRATION.md](RFID_INTEGRATION.md)
- [COMPONENT_STATUS.md](COMPONENT_STATUS.md)
- [ARCHITECTURE_REFACTORING.md](ARCHITECTURE_REFACTORING.md)

---

## 📊 Statistics

| Category | Files | Size |
|----------|-------|------|
| User Guides | 8 | ~42K |
| Architecture | 4 | ~78K |
| Future Design | 3 | ~56K |
| Planning | 1 | ~9K |
| **Total in docs/** | **16** | **~185K** |

Plus 3 files in root (README, DOCS_INDEX, INSTALL) = **19 files total**

---

## 💡 Tips

1. **Start with SYSTEM_ARCHITECTURE.md** for technical deep dive
2. **Use DOCS_INDEX.md** in root for quick navigation
3. **Check COMPONENT_STATUS.md** to see what's real vs planned
4. **Dotted boxes** in diagrams = future/unimplemented components
5. **All guides include working examples** you can copy-paste

---

**Last updated**: December 27, 2025  
**Primary reference**: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) (48K)  
**Complete index**: [../DOCS_INDEX.md](../DOCS_INDEX.md)
