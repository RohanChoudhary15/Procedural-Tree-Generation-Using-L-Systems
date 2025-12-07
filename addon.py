
bl_info = {
    "name": "L-System Tree Generator",
    "author": "Procedural Tree Generator",
    "version": (1, 2, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > L-System Tree",
    "description": "Generate 3D procedural trees using Lindenmayer systems with presets",
    "category": "Add Mesh",
}

import bpy
import bmesh
from mathutils import Matrix, Vector, Euler
import random
import math


TREE_PRESETS = {
    'CLASSIC': {
        'name': 'Classic',
        'axiom': 'X',
        'rules': 'X:F[+X]F[-X]FX\nF:FF',
        'angle': 20.0,
        'iterations': 6,
        'initial_length': 1.0,
        'length_decay': 0.88,
        'initial_radius': 1.0,
        'radius_decay': 0.9,
        'bevel_depth': 0.05,
    },
    'PINE': {
        'name': 'Pine',
        'axiom': 'X',
        'rules': 'X:F[+X][-X]FX\nF:FF',
        'angle': 18.0,
        'iterations': 7,
        'initial_length': 1.0,
        'length_decay': 0.93,
        'initial_radius': 1.0,
        'radius_decay': 0.92,
        'bevel_depth': 0.05,
    },
    'BROADLEAF': {
        'name': 'Broadleaf',
        'axiom': 'F',
        'rules': 'F:F[+F]F[-F][F]',
        'angle': 22.0,
        'iterations': 5,
        'initial_length': 1.0,
        'length_decay': 0.82,
        'initial_radius': 1.0,
        'radius_decay': 0.88,
        'bevel_depth': 0.05,
    },
    'OAK': {
        'name': 'Oak',
        'axiom': 'X',
        'rules': 'X:F-[[X]+X]+F[+FX]-X\nF:FF',
        'angle': 25.0,
        'iterations': 6,
        'initial_length': 1.0,
        'length_decay': 0.88,
        'initial_radius': 1.0,
        'radius_decay': 0.88,
        'bevel_depth': 0.05,
    },
    'FANTASY': {
        'name': 'Fantasy Dense',
        'axiom': 'X',
        'rules': 'X:F[+X][-X]F[+X]F[-X]X\nF:FF',
        'angle': 18.0,
        'iterations': 7,
        'initial_length': 1.0,
        'length_decay': 0.94,
        'initial_radius': 1.0,
        'radius_decay': 0.92,
        'bevel_depth': 0.05,
    },
    'BUSH': {
        'name': 'Explosive Bush',
        'axiom': 'X',
        'rules': 'X:FX[+X][-X]FX\nF:F[F]F',
        'angle': 16.0,
        'iterations': 5,
        'initial_length': 1.0,
        'length_decay': 0.9,
        'initial_radius': 1.0,
        'radius_decay': 0.9,
        'bevel_depth': 0.05,
    },
}


class TurtleState:
    def __init__(self, position, orientation, length, radius):
        self.position = position.copy()
        self.orientation = orientation.copy()
        self.length = length
        self.radius = radius


class Turtle3D:
    def __init__(self, angle, initial_length, initial_radius, length_decay, radius_decay, rotation_jitter, length_jitter, tropism_strength, seed, branch_spread):
        self.position = Vector((0, 0, 0))
        self.orientation = Matrix.Identity(3)
        self.angle = math.radians(angle)
        self.current_length = initial_length
        self.current_radius = initial_radius
        self.length_decay = length_decay
        self.radius_decay = radius_decay
        self.rotation_jitter = math.radians(rotation_jitter)
        self.length_jitter = length_jitter
        self.tropism_strength = tropism_strength
        self.branch_spread = math.radians(branch_spread)
        self.stack = []
        self.branches = []
        self.leaf_positions = []
        self.leaf_orientations = []
        self.current_branch_points = []
        random.seed(seed)
    
    def get_forward(self):
        return (self.orientation @ Vector((0, 0, 1))).normalized()
    
    def get_left(self):
        return (self.orientation @ Vector((1, 0, 0))).normalized()
    
    def get_up(self):
        return (self.orientation @ Vector((0, 1, 0))).normalized()
    
    def apply_tropism(self):
        if self.tropism_strength > 0:
            tropism_direction = Vector((0, 0, 1))
            forward = self.get_forward()
            
            correction_axis = forward.cross(tropism_direction)
            
            if correction_axis.length > 0.0001:
                correction_axis.normalize()
                angle = self.tropism_strength * self.current_length * 0.1
                rot_matrix = Matrix.Rotation(angle, 3, correction_axis)
                self.orientation = rot_matrix @ self.orientation
    
    def rotate_local(self, angle, local_axis):
        jitter = random.uniform(-self.rotation_jitter, self.rotation_jitter)
        total_angle = angle + jitter
        
        world_axis = (self.orientation @ local_axis).normalized()
        
        rot_matrix = Matrix.Rotation(total_angle, 3, world_axis)
        self.orientation = rot_matrix @ self.orientation
    
    def yaw_right(self):
        # Add random Y-axis spread for 3D branching
        y_spread = random.uniform(-self.branch_spread, self.branch_spread)
        self.rotate_local(y_spread, Vector((0, 1, 0)))
        self.rotate_local(self.angle, Vector((0, 1, 0)))
    
    def yaw_left(self):
        # Add random Y-axis spread for 3D branching
        y_spread = random.uniform(-self.branch_spread, self.branch_spread)
        self.rotate_local(y_spread, Vector((0, 1, 0)))
        self.rotate_local(-self.angle, Vector((0, 1, 0)))
    
    def pitch_down(self):
        self.rotate_local(self.angle, Vector((1, 0, 0)))
    
    def pitch_up(self):
        self.rotate_local(-self.angle, Vector((1, 0, 0)))
    
    def roll_left(self):
        self.rotate_local(self.angle, Vector((0, 0, 1)))
    
    def roll_right(self):
        self.rotate_local(-self.angle, Vector((0, 0, 1)))
    
    def turn_around(self):
        self.rotate_local(math.pi, Vector((0, 1, 0)))
    
    def forward(self, draw=True):
        jitter = 1.0 + random.uniform(-self.length_jitter, self.length_jitter)
        step_length = self.current_length * jitter
        
        self.apply_tropism()
        
        start_pos = self.position.copy()
        start_radius = self.current_radius
        
        forward_vec = self.get_forward()
        self.position += forward_vec * step_length
        
        if draw:
            self.current_branch_points.append((start_pos.copy(), start_radius))
            
            new_length = self.current_length * self.length_decay
            new_radius = self.current_radius * self.radius_decay
            
            self.current_branch_points.append((self.position.copy(), new_radius))
            
            self.current_length = new_length
            self.current_radius = new_radius
        else:
            self.current_length *= self.length_decay
            self.current_radius *= self.radius_decay
    
    def push(self):
        state = TurtleState(self.position, self.orientation, self.current_length, self.current_radius)
        self.stack.append(state)
        
        # Apply random rotation around Z-axis (roll) when branching for full 3D spread
        random_roll = random.uniform(0, math.pi * 2)
        self.rotate_local(random_roll, Vector((0, 0, 1)))
        
        if len(self.current_branch_points) > 0:
            self.branches.append(self.current_branch_points[:])
            self.current_branch_points = []
    
    def pop(self):
        if len(self.current_branch_points) > 0:
            self.branches.append(self.current_branch_points[:])
            self.current_branch_points = []
        
        if self.stack:
            state = self.stack.pop()
            self.position = state.position.copy()
            self.orientation = state.orientation.copy()
            self.current_length = state.length
            self.current_radius = state.radius
    
    def add_leaf(self):
        self.leaf_positions.append(self.position.copy())
        self.leaf_orientations.append(self.orientation.copy())
    
    def finalize(self):
        if len(self.current_branch_points) > 0:
            self.branches.append(self.current_branch_points[:])


def expand_lsystem(axiom, rules, iterations):
    current = axiom
    rules_dict = {}
    
    for rule in rules.split('\n'):
        rule = rule.strip()
        if ':' in rule:
            parts = rule.split(':', 1)
            if len(parts) == 2:
                symbol = parts[0].strip()
                replacement = parts[1].strip()
                rules_dict[symbol] = replacement
    
    for _ in range(iterations):
        next_string = ""
        for char in current:
            if char in rules_dict:
                next_string += rules_dict[char]
            else:
                next_string += char
        current = next_string
    
    return current


def interpret_lsystem(lstring, turtle):
    for char in lstring:
        if char == 'F':
            turtle.forward(draw=True)
        elif char == 'f':
            turtle.forward(draw=False)
        elif char == '+':
            turtle.yaw_right()
        elif char == '-':
            turtle.yaw_left()
        elif char == '&':
            turtle.pitch_down()
        elif char == '^':
            turtle.pitch_up()
        elif char == '\\':
            turtle.roll_left()
        elif char == '/':
            turtle.roll_right()
        elif char == '|':
            turtle.turn_around()
        elif char == '[':
            turtle.push()
        elif char == ']':
            turtle.pop()
            turtle.add_leaf()
    
    turtle.finalize()


def create_branch_curve(points, name, bevel_depth):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 3
    curve_data.resolution_u = 12
    curve_data.fill_mode = 'FULL'
    
    spline = curve_data.splines.new(type='BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, (pos, radius) in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = pos
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        bp.radius = radius
    
    curve_obj = bpy.data.objects.new(name, curve_data)
    return curve_obj


def create_leaf_mesh(size):
    mesh = bpy.data.meshes.new("Leaf_Mesh")
    bm = bmesh.new()
    
    # Create a more detailed leaf shape with center vein
    verts = [
        # Base of leaf
        bm.verts.new(Vector((0, 0, 0))),
        # Left side points
        bm.verts.new(Vector((-size * 0.15, 0, size * 0.2))),
        bm.verts.new(Vector((-size * 0.35, 0, size * 0.4))),
        bm.verts.new(Vector((-size * 0.3, 0, size * 0.6))),
        bm.verts.new(Vector((-size * 0.15, 0, size * 0.8))),
        # Tip
        bm.verts.new(Vector((0, 0, size))),
        # Right side points
        bm.verts.new(Vector((size * 0.15, 0, size * 0.8))),
        bm.verts.new(Vector((size * 0.3, 0, size * 0.6))),
        bm.verts.new(Vector((size * 0.35, 0, size * 0.4))),
        bm.verts.new(Vector((size * 0.15, 0, size * 0.2))),
    ]
    
    # Create faces for the leaf
    faces_indices = [
        [0, 1, 2],
        [0, 2, 3],
        [0, 3, 4],
        [0, 4, 5],
        [0, 5, 6],
        [0, 6, 7],
        [0, 7, 8],
        [0, 8, 9],
    ]
    
    for face_idx in faces_indices:
        bm.faces.new([verts[i] for i in face_idx])
    
    bm.to_mesh(mesh)
    bm.free()
    
    return mesh


def create_bark_material():
    """Create a procedural bark material"""
    mat = bpy.data.materials.new(name="Bark_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Create nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Roughness'].default_value = 0.9
    principled.inputs['Specular IOR Level'].default_value = 0.3
    
    # Color ramp for bark color variation
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-400, 100)
    color_ramp.color_ramp.elements[0].color = (0.1, 0.06, 0.03, 1)  # Dark brown
    color_ramp.color_ramp.elements[1].color = (0.25, 0.15, 0.08, 1)  # Light brown
    
    # Noise texture for variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-600, 100)
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    
    # Bump for bark texture
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (-200, -200)
    bump.inputs['Strength'].default_value = 0.3
    
    noise_bump = nodes.new(type='ShaderNodeTexNoise')
    noise_bump.location = (-400, -200)
    noise_bump.inputs['Scale'].default_value = 15.0
    noise_bump.inputs['Detail'].default_value = 10.0
    
    # Connect nodes
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(noise_bump.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_leaf_material():
    """Create a leaf material with gradient and subsurface scattering"""
    mat = bpy.data.materials.new(name="Leaf_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Create nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Roughness'].default_value = 0.4
    principled.inputs['Subsurface Weight'].default_value = 0.1
    principled.inputs['Subsurface Radius'].default_value = (0.1, 0.3, 0.1)
    
    # Gradient for leaf color variation (darker at base, lighter at tip)
    gradient = nodes.new(type='ShaderNodeTexGradient')
    gradient.location = (-600, 200)
    gradient.gradient_type = 'LINEAR'
    
    # Texture coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 200)
    
    # Color ramp for green gradient
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-400, 200)
    color_ramp.color_ramp.elements[0].color = (0.05, 0.15, 0.02, 1)  # Dark green
    color_ramp.color_ramp.elements[1].color = (0.2, 0.6, 0.1, 1)  # Bright green
    
    # Noise for variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-600, -100)
    noise.inputs['Scale'].default_value = 10.0
    noise.inputs['Detail'].default_value = 5.0
    
    # Mix color variation
    mix_rgb = nodes.new(type='ShaderNodeMix')
    mix_rgb.location = (-200, 100)
    mix_rgb.data_type = 'RGBA'
    mix_rgb.inputs['Factor'].default_value = 0.3
    
    # Connect nodes
    links.new(tex_coord.outputs['Object'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix_rgb.inputs['A'])
    links.new(noise.outputs['Fac'], mix_rgb.inputs['B'])
    links.new(mix_rgb.outputs['Result'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def create_tree(axiom, rules, iterations, angle, initial_length, length_decay, 
                initial_radius, radius_decay, bevel_depth, rotation_jitter, 
                length_jitter, tropism_strength, seed, add_leaves, leaf_size, leaf_jitter, branch_spread):
    
    lstring = expand_lsystem(axiom, rules, iterations)
    
    turtle = Turtle3D(angle, initial_length, initial_radius, length_decay, 
                      radius_decay, rotation_jitter, length_jitter, tropism_strength, seed, branch_spread)
    
    interpret_lsystem(lstring, turtle)
    
    collection_name = "L-System Tree"
    if collection_name in bpy.data.collections:
        old_collection = bpy.data.collections[collection_name]
        for obj in list(old_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_collection)
    
    tree_collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(tree_collection)
    
    # Create materials
    bark_material = create_bark_material()
    leaf_material = create_leaf_material()
    
    # Create branches with bark material
    for i, branch_points in enumerate(turtle.branches):
        if len(branch_points) >= 2:
            curve_obj = create_branch_curve(branch_points, f"Branch_{i}", bevel_depth)
            
            # Apply bark material
            if curve_obj.data.materials:
                curve_obj.data.materials[0] = bark_material
            else:
                curve_obj.data.materials.append(bark_material)
            
            tree_collection.objects.link(curve_obj)
    
    if add_leaves and len(turtle.leaf_positions) > 0:
        leaf_mesh = create_leaf_mesh(leaf_size)
        leaf_template = bpy.data.objects.new("Leaf_Template", leaf_mesh)
        tree_collection.objects.link(leaf_template)
        leaf_template.hide_viewport = True
        leaf_template.hide_render = True
        
        random.seed(seed + 1)
        
        for i, (leaf_pos, leaf_orientation) in enumerate(zip(turtle.leaf_positions, turtle.leaf_orientations)):
            leaf_instance = bpy.data.objects.new(f"Leaf_{i}", leaf_mesh)
            
            # Apply leaf material
            if leaf_instance.data.materials:
                leaf_instance.data.materials[0] = leaf_material
            else:
                leaf_instance.data.materials.append(leaf_material)
            
            jitter_pos = leaf_pos + Vector((
                random.uniform(-leaf_jitter, leaf_jitter),
                random.uniform(-leaf_jitter, leaf_jitter),
                random.uniform(-leaf_jitter, leaf_jitter)
            ))
            
            leaf_instance.location = jitter_pos
            
            forward = (leaf_orientation @ Vector((0, 0, 1))).normalized()
            up = (leaf_orientation @ Vector((0, 1, 0))).normalized()
            
            rotation_matrix = leaf_orientation.to_4x4()
            leaf_instance.matrix_world = rotation_matrix
            leaf_instance.location = jitter_pos
            
            random_twist = Euler((
                random.uniform(-0.3, 0.3),
                random.uniform(-0.3, 0.3),
                random.uniform(0, math.pi * 2)
            ), 'XYZ')
            
            leaf_instance.rotation_euler.rotate(random_twist)
            
            # Set smooth shading for leaves
            for poly in leaf_instance.data.polygons:
                poly.use_smooth = True
            
            tree_collection.objects.link(leaf_instance)
    
    return tree_collection


class LSYSTEM_OT_generate_tree(bpy.types.Operator):
    bl_idname = "lsystem.generate_tree"
    bl_label = "Generate Tree"
    bl_description = "Generate a 3D tree using L-system"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.lsystem_props
        
        try:
            create_tree(
                axiom=props.axiom,
                rules=props.rules,
                iterations=props.iterations,
                angle=props.angle,
                initial_length=props.initial_length,
                length_decay=props.length_decay,
                initial_radius=props.initial_radius,
                radius_decay=props.radius_decay,
                bevel_depth=props.bevel_depth,
                rotation_jitter=props.rotation_jitter,
                length_jitter=props.length_jitter,
                tropism_strength=props.tropism_strength,
                seed=props.seed,
                add_leaves=props.add_leaves,
                leaf_size=props.leaf_size,
                leaf_jitter=props.leaf_jitter,
                branch_spread=props.branch_spread
            )
            self.report({'INFO'}, "Tree generated successfully")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate tree: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class LSYSTEM_PT_main_panel(bpy.types.Panel):
    bl_label = "L-System Tree"
    bl_idname = "LSYSTEM_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "L-System Tree"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.lsystem_props
        
        box = layout.box()
        box.label(text="Tree Presets", icon='PRESET')
        box.prop(props, "tree_preset", text="")
        
        box = layout.box()
        box.label(text="L-System Rules", icon='OUTLINER_OB_CURVE')
        box.prop(props, "axiom")
        box.prop(props, "rules")
        box.prop(props, "iterations")
        
        box = layout.box()
        box.label(text="Turtle Settings", icon='ORIENTATION_GIMBAL')
        box.prop(props, "angle")
        box.prop(props, "initial_length")
        box.prop(props, "length_decay")
        box.prop(props, "initial_radius")
        box.prop(props, "radius_decay")
        box.prop(props, "bevel_depth")
        
        box = layout.box()
        box.label(text="3D Branching", icon='EMPTY_AXIS')
        box.prop(props, "branch_spread")
        
        box = layout.box()
        box.label(text="Variation", icon='FORCE_TURBULENCE')
        box.prop(props, "rotation_jitter")
        box.prop(props, "length_jitter")
        box.prop(props, "tropism_strength")
        box.prop(props, "seed")
        
        box = layout.box()
        box.label(text="Leaves", icon='OUTLINER_OB_MESH')
        box.prop(props, "add_leaves")
        if props.add_leaves:
            box.prop(props, "leaf_size")
            box.prop(props, "leaf_jitter")
        
        layout.separator()
        layout.operator("lsystem.generate_tree", icon='CURVE_BEZCURVE')


def apply_preset(self, context):
    props = context.scene.lsystem_props
    preset_key = props.tree_preset
    
    if preset_key in TREE_PRESETS:
        preset = TREE_PRESETS[preset_key]
        
        props.axiom = preset['axiom']
        props.rules = preset['rules']
        props.angle = preset['angle']
        props.iterations = preset['iterations']
        props.initial_length = preset['initial_length']
        props.length_decay = preset['length_decay']
        props.initial_radius = preset['initial_radius']
        props.radius_decay = preset['radius_decay']
        props.bevel_depth = preset['bevel_depth']


class LSystemProperties(bpy.types.PropertyGroup):
    tree_preset: bpy.props.EnumProperty(
        name="Tree Type",
        description="Select a predefined tree preset",
        items=[
            ('CLASSIC', 'Classic', 'Classic branching tree'),
            ('PINE', 'Pine', 'Pine-like coniferous tree'),
            ('BROADLEAF', 'Broadleaf', 'Broad-leafed deciduous tree'),
            ('OAK', 'Oak', 'Oak-style tree with complex branching'),
            ('FANTASY', 'Fantasy Dense', 'Dense fantasy tree with many branches'),
            ('BUSH', 'Explosive Bush', 'Bush-like structure with explosive branching'),
        ],
        default='CLASSIC',
        update=apply_preset
    )
    
    axiom: bpy.props.StringProperty(
        name="Axiom",
        description="Starting string for the L-system",
        default="X"
    )
    
    rules: bpy.props.StringProperty(
        name="Rules",
        description="Production rules (format: X:F[+X]F[-X]+X)",
        default="X:F[+X]F[-X]FX\nF:FF"
    )
    
    iterations: bpy.props.IntProperty(
        name="Iterations",
        description="Number of L-system iterations",
        default=6,
        min=1,
        max=10
    )
    
    angle: bpy.props.FloatProperty(
        name="Angle",
        description="Branching angle in degrees",
        default=20.0,
        min=0.0,
        max=180.0
    )
    
    initial_length: bpy.props.FloatProperty(
        name="Initial Length",
        description="Starting segment length",
        default=1.0,
        min=0.01,
        max=100.0
    )
    
    length_decay: bpy.props.FloatProperty(
        name="Length Decay",
        description="Length multiplier per segment",
        default=0.88,
        min=0.1,
        max=1.0
    )
    
    initial_radius: bpy.props.FloatProperty(
        name="Initial Radius",
        description="Starting branch radius",
        default=1.0,
        min=0.01,
        max=10.0
    )
    
    radius_decay: bpy.props.FloatProperty(
        name="Radius Decay",
        description="Radius multiplier per segment",
        default=0.9,
        min=0.1,
        max=1.0
    )
    
    bevel_depth: bpy.props.FloatProperty(
        name="Bevel Thickness",
        description="Curve bevel depth",
        default=0.05,
        min=0.001,
        max=1.0
    )
    
    branch_spread: bpy.props.FloatProperty(
        name="Branch Spread (Y-axis)",
        description="Random Y-axis spread for full 3D branching (degrees)",
        default=30.0,
        min=0.0,
        max=180.0
    )
    
    rotation_jitter: bpy.props.FloatProperty(
        name="Rotation Jitter",
        description="Random rotation variance in degrees",
        default=5.0,
        min=0.0,
        max=45.0
    )
    
    length_jitter: bpy.props.FloatProperty(
        name="Length Jitter",
        description="Random length variance (fraction)",
        default=0.1,
        min=0.0,
        max=0.5
    )
    
    tropism_strength: bpy.props.FloatProperty(
        name="Tropism Strength",
        description="Gravitropic bias strength",
        default=0.05,
        min=0.0,
        max=1.0
    )
    
    seed: bpy.props.IntProperty(
        name="Random Seed",
        description="Seed for random variations",
        default=42,
        min=0
    )
    
    add_leaves: bpy.props.BoolProperty(
        name="Add Leaves",
        description="Add leaves at branch tips",
        default=True
    )
    
    leaf_size: bpy.props.FloatProperty(
        name="Leaf Size",
        description="Size of leaf meshes",
        default=0.3,
        min=0.01,
        max=5.0
    )
    
    leaf_jitter: bpy.props.FloatProperty(
        name="Leaf Jitter",
        description="Random position offset for leaves",
        default=0.1,
        min=0.0,
        max=2.0
    )


classes = (
    LSystemProperties,
    LSYSTEM_OT_generate_tree,
    LSYSTEM_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.lsystem_props = bpy.props.PointerProperty(type=LSystemProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.lsystem_props


if __name__ == "__main__":
    register()

