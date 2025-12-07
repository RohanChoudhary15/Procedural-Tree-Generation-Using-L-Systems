# 🌳 L-System Tree Generator (Blender Add-on)

A powerful procedural tree generator for Blender that uses **Lindenmayer Systems (L-Systems)** to create natural, customizable, and fully 3D branching structures.  
This add-on provides a set of presets (Classic, Pine, Broadleaf, Oak, Fantasy, Bush) and extensive controls for branching angles, randomness, tropism, leaf generation, and procedural materials.

---

## ✨ Features

- ✔️ Fully procedural tree creation using **L-Systems**  
- ✔️ Multiple **tree presets** for quick generation  
- ✔️ Control over branching structure, randomness, tropism, and decay  
- ✔️ Real 3D turtle interpreter supporting yaw, pitch, roll & branch stacks  
- ✔️ **Procedural bark material** & **procedural leaf material**  
- ✔️ Automatic generation of curve-based branches with beveling  
- ✔️ Optional leaf instancing with jitter & orientation  
- ✔️ Clean UI integrated into **3D View > Sidebar > L-System Tree**  
- ✔️ Fast regeneration with undo support  


---

## 🔧 Installation

1. Download the addon.py or the copy the contents.  
2. In Blender, go to:  
   **Scripting → Create a new script**  
3. Paste the contents and Execute the script. 
4. Access the tool from:  
   **3D View → Sidebar (N) → L-System Tree**

---

## 🧠 How It Works

This plugin uses **Lindenmayer systems**, a string-rewriting algorithm often used to simulate natural growth (plants, trees, corals, etc.).

### Step-by-step process:

1. **Expand the L-System:**  
   - The axiom and rules generate a long string via iterative rewriting.

2. **Interpretation via a 3D Turtle:**  
   - The string is processed character-by-character.  
   - Commands like `F`, `+`, `-`, `[`, `]` map to movement, rotation, and branch control.

3. **Branches are created as 3D curves:**  
   - Collected points are turned into Bézier curves.  
   - A bevel depth creates rounded branches.

4. **Leaves:**  
   - When a `]` (pop) is processed, a leaf is recorded and later instantiated.

5. **Procedural Materials:**  
   - Bark uses noise, bumps, and color variations  
   - Leaves use gradients, SSS, and noise blending to simulate translucency.

6. **Final Output:**  
   - All objects are grouped into a new Collection named **"L-System Tree"**.

---

## 📚 Concepts Used

### **1. Lindenmayer Systems (L-Systems)**
- String rewriting system  
- Axiom (start) + rules (rewrites)  
- Produces structural patterns from simple grammar

### **2. Turtle Graphics**
- 3D position & orientation represented by a transformation matrix  
- Commands:
  - `F` – move forward and draw  
  - `+/-` – yaw  
  - `&/^` – pitch  
  - `\` `/` – roll  
  - `|` – turn around  
  - `[` – push state  
  - `]` – pop state + create leaf

### **3. Tropism**
Simulates a biological lean toward gravity/light by applying rotational bias.

### **4. Mesh & Curve Generation**
- Branches generated as **Bezier curves** with radius & bevel  
- Leaves generated as low-poly meshes  
- Smoothing and material assignment handled automatically

### **5. Procedural Shading (Cycles/Eevee)**
- Bark: noise → color ramp → Bump mapping → Principled  
- Leaves: gradient → noise → color mix → SSS

### **6. Randomization / Jitter**
Used to break symmetry:
- Rotation jitter  
- Length jitter  
- Leaf position jitter  
- Branch spread for full 3D randomness

---

## 🧩 Addon Panels & Controls

The add-on exposes the following control groups:

### **Tree Presets**
Choose from:
- Classic  
- Pine  
- Broadleaf  
- Oak  
- Fantasy Dense  
- Explosive Bush  

### **L-System Parameters**
- Axiom  
- Rules  
- Iterations  

### **Turtle Settings**
- Angle  
- Length decay  
- Radius decay  
- Bevel depth  
- Initial branch size  

### **3D Branching**
- Branch spread (random Y-axis rotation)

### **Variation**
- Rotation jitter  
- Length jitter  
- Tropism strength  
- Random seed  

### **Leaves**
- Toggle leaves  
- Leaf size  
- Leaf jitter  

---

## 🌲 Tree Presets

| Preset | Description |
|--------|-------------|
| **Classic** | Balanced branching suitable for many trees |
| **Pine** | Tall conifer style with narrow angles |
| **Broadleaf** | Full deciduous silhouette |
| **Oak** | More chaotic structure with depth |
| **Fantasy Dense** | Overgrown magical tree |
| **Explosive Bush** | Dense shrub-like growth |

Each preset configures:
- Axiom  
- Rules  
- Angle  
- Iterations  
- Length/radius decay  
- Bevel depth  

---

## ⚠️ Known Limitations

- Extremely high iteration counts may produce large strings (slow).  
- Branch curves are not converted to mesh unless user applies modifier.  
- Leaf count increases rapidly for dense rules.  
- Very high jitter values may produce tangled shapes.  

---

## 📄 License

This project is released under the **MIT License**.  
You are free to modify and use it in personal or commercial projects.

---

## 💬 Feedback & Contributions

Pull requests, improvements, bug reports, and new presets are welcome!


