# bankers-algorithm-simulator
A graphical Python tool demonstrating the Banker's Algorithm for deadlock avoidance. Users can input resource matrices, compute safe sequences, validate process requests, and visualize execution flow. Built with Tkinter, it provides an interactive and educational simulator ideal for OS learning and teaching.
# 🏦 Banker's Algorithm Simulator (Python + Tkinter)

A complete GUI-based simulation of the **Banker's Algorithm**, used in operating systems for deadlock avoidance.  
This tool allows users to:

✔ Input Allocation, Max, Need, Total, and Available matrices  
✔ Perform step-by-step **Safety Algorithm** visualization  
✔ Submit resource requests and test if the system stays safe  
✔ View detailed logs and a **Gantt chart** style safe sequence  

---

## 📌 Features

### 🔹 Dynamic Table Generation
Automatically creates input tables based on:
- Number of Processes (P)
- Number of Resource Types (R)

### 🔹 Full Banker's Algorithm Support
Includes:
- **Safety Algorithm**
- **Resource Request Algorithm**
- Automatic **Need matrix calculation**

### 🔹 Visual Output
- **Step-by-step reasoning logs**
- Color-coded success/failure messages
- **Gantt chart** showing the safe sequence

### 🔹 Data Tools
- Load **sample OS textbook data**
- Generate **random valid tables**
- Auto-calculate “Available” = Total – Allocation
- Reset fields instantly

---

## 🚀 Getting Started

### **1. Requirements**
Install Python (3.8 or later recommended)

Required library:
tkinter (comes pre-installed with Python)

### **2. Run the Program**
Run the main Python file:

```bash
python bankers_gui.py
```
#🖼 Screenshots
/screenshots/main_window.png
/screenshots/log_output.png


📘 How It Works (Short Explanation)
Banker's Algorithm Components

    Allocation: Current allocated resources for each process
    Max: Maximum demand of each process
    Need = Max – Allocation
    Available: Resources currently free
    Safety Check
    The system is safe if all processes can eventually finish.

Request Algorithm

    A request from process Pi is granted only if:
    Request ≤ Need
    Request ≤ Available
    System remains in a safe state after provisional allocation

🎯 Demo Workflow

    Enter number of Processes (P) and Resources (R)    
    Click Generate Table    
    Fill Allocation and Max    
    Enter Total or Available    
    Click Check Safety & Show Steps    
    Submit a request to test safety

📄 License:  This project is open-source under the MIT License.
