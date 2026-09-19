import math

def generate_svg():
    width = 300
    height = 300
    frames = 120
    
    # 16 vertices of a tesseract
    vertices = []
    for i in range(16):
        x = -1 if (i & 1) == 0 else 1
        y = -1 if (i & 2) == 0 else 1
        z = -1 if (i & 4) == 0 else 1
        w = -1 if (i & 8) == 0 else 1
        vertices.append((x, y, z, w))
        
    # 32 edges
    edges = []
    for i in range(16):
        for j in range(i + 1, 16):
            # Differ by exactly 1 bit
            if bin(i ^ j).count('1') == 1:
                edges.append((i, j))
                
    # We will generate the 2D coordinates for each vertex at each frame
    vertex_frames = {i: [] for i in range(16)}
    
    for f in range(frames):
        # Rotate in XW and YW planes
        theta = (f / frames) * 2 * math.pi
        
        for i, (x, y, z, w) in enumerate(vertices):
            # 4D Rotation (Double rotation)
            x_rot = x * math.cos(theta) - w * math.sin(theta)
            w_rot = x * math.sin(theta) + w * math.cos(theta)
            
            y_rot = y * math.cos(theta/2) - z * math.sin(theta/2)
            z_rot = y * math.sin(theta/2) + z * math.cos(theta/2)
            
            # 4D to 3D perspective projection
            distance_4d = 2.5
            w_factor = 1 / (distance_4d - w_rot)
            
            x_3d = x_rot * w_factor
            y_3d = y_rot * w_factor
            z_3d = z_rot * w_factor
            
            # Static 3D rotation for better viewing angle
            angle_x = math.pi / 4
            angle_y = math.pi / 4
            
            # Rotate Y
            x_3d_rot = x_3d * math.cos(angle_y) - z_3d * math.sin(angle_y)
            z_3d_rot = x_3d * math.sin(angle_y) + z_3d * math.cos(angle_y)
            
            # Rotate X
            y_3d_rot = y_3d * math.cos(angle_x) - z_3d_rot * math.sin(angle_x)
            z_final = y_3d * math.sin(angle_x) + z_3d_rot * math.cos(angle_x)
            
            # 3D to 2D projection
            distance_3d = 4.0
            z_factor = 1 / (distance_3d - z_final)
            
            x_2d = x_3d_rot * z_factor
            y_2d = y_3d_rot * z_factor
            
            # Scale to SVG size
            scale = 300
            px = width / 2 + x_2d * scale
            py = height / 2 + y_2d * scale
            
            vertex_frames[i].append((px, py))
            
    # Build the SVG
    svg = []
    svg.append(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')
    
    # We can add a subtle glow effect with SVG filters
    svg.append('''
    <defs>
      <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    ''')
    
    for edge in edges:
        v1, v2 = edge
        x1_vals = ";".join([f"{vertex_frames[v1][f][0]:.2f}" for f in range(frames)])
        y1_vals = ";".join([f"{vertex_frames[v1][f][1]:.2f}" for f in range(frames)])
        x2_vals = ";".join([f"{vertex_frames[v2][f][0]:.2f}" for f in range(frames)])
        y2_vals = ";".join([f"{vertex_frames[v2][f][1]:.2f}" for f in range(frames)])
        
        # Add the first value to the end to close the loop smoothly
        x1_vals += f";{vertex_frames[v1][0][0]:.2f}"
        y1_vals += f";{vertex_frames[v1][0][1]:.2f}"
        x2_vals += f";{vertex_frames[v2][0][0]:.2f}"
        y2_vals += f";{vertex_frames[v2][0][1]:.2f}"
        
        line = f'<line stroke="#0F766E" stroke-width="2.5" filter="url(#glow)">'
        line += f'<animate attributeName="x1" values="{x1_vals}" dur="8s" repeatCount="indefinite" />'
        line += f'<animate attributeName="y1" values="{y1_vals}" dur="8s" repeatCount="indefinite" />'
        line += f'<animate attributeName="x2" values="{x2_vals}" dur="8s" repeatCount="indefinite" />'
        line += f'<animate attributeName="y2" values="{y2_vals}" dur="8s" repeatCount="indefinite" />'
        line += '</line>'
        svg.append(line)
        
    svg.append('</svg>')
    
    with open('tesseract.svg', 'w') as f:
        f.write("\\n".join(svg))
        
if __name__ == '__main__':
    generate_svg()
