"""Simple 3D model generator (OBJ exporter).

Usage:
  python scripts/generate_3d_model.py --type cube --size 1 --out assets/models/sample_cube.obj

Generates basic primitives: cube, uv_sphere (latitude/longitude), cylinder.
This is minimal and doesn't require external 3D libraries.
"""
import argparse
import math
import os


def write_obj(vertices, faces, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    base = os.path.splitext(out_path)[0]
    mtl_name = os.path.basename(base) + '.mtl'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"mtllib {mtl_name}\n")
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        # optional: uvs stored on faces as tuple (face_idx, [uvs]) when present
        # caller must write vt lines before faces if uvs present
        for face in faces:
            # faces can be tuples of ints or tuples of (v, vt) pairs
            if len(face) == 0:
                continue
            if isinstance(face[0], tuple):
                # face contains pairs (v_idx, vt_idx)
                f.write("f " + " ".join(f"{v}/{vt}" for v, vt in face) + "\n")
            else:
                f.write("f " + " ".join(str(i) for i in face) + "\n")
    # write a basic MTL if texture info will be expected
    mtl_path = base + '.mtl'
    if not os.path.exists(mtl_path):
        with open(mtl_path, 'w', encoding='utf-8') as mf:
            mf.write("newmtl material_0\n")
            mf.write("Ka 1.000 1.000 1.000\n")
            mf.write("Kd 1.000 1.000 1.000\n")
            mf.write("Ks 0.000 0.000 0.000\n")
            mf.write("d 1.0\n")
            mf.write("illum 2\n")
            mf.write("map_Kd texture.png\n")


def generate_cube(size=1.0):
    s = size / 2.0
    verts = [
        (-s, -s, -s),
        ( s, -s, -s),
        ( s,  s, -s),
        (-s,  s, -s),
        (-s, -s,  s),
        ( s, -s,  s),
        ( s,  s,  s),
        (-s,  s,  s),
    ]
    faces = [
        (1,2,3,4),
        (5,8,7,6),
        (1,5,6,2),
        (2,6,7,3),
        (3,7,8,4),
        (5,1,4,8),
    ]
    return verts, faces


def generate_cube_with_uv(size=1.0):
    verts, faces = generate_cube(size=size)
    # simple UVs for cube: 14 vt coords and faces referencing vt indices
    # We'll create 24 vertices in UV-mapped mode (duplicate vertex per face corner)
    vlist = []
    vtlist = []
    face_vt = []
    # define per-face positions and UVs
    face_definitions = [
        # bottom
        ([-0.5,-0.5,-0.5],[0,0]),([0.5,-0.5,-0.5],[1,0]),([0.5,0.5,-0.5],[1,1]),([-0.5,0.5,-0.5],[0,1]),
        # top
        ([-0.5,-0.5,0.5],[0,0]),([-0.5,0.5,0.5],[0,1]),([0.5,0.5,0.5],[1,1]),([0.5,-0.5,0.5],[1,0]),
        # front
    ]
    # Simpler approach: reuse existing cube verts but assign 24 vt entries mapping each face.
    # Create vt coords (per face corner) and produce face tuples as (v_idx, vt_idx)
    vt_index = 1
    faces_with_vt = []
    # faces defined earlier correspond to indices in verts (1..8)
    # for each face, create vt entries for its four corners
    for face in faces:
        face_pairs = []
        for vi in face:
            # vertex position
            pos = verts[vi-1]
            vlist.append(pos)
            # simple planar UV by projecting to XZ or XY depending on normal
            # We'll use a generic mapping: use x,z as uv
            u = (pos[0] + 0.5)
            v = (pos[2] + 0.5)
            vtlist.append((u, v))
            face_pairs.append((len(vlist), len(vtlist)))
        faces_with_vt.append(tuple(face_pairs))
    return vlist, faces_with_vt, vtlist


def generate_uv_sphere(radius=1.0, lat_segments=12, lon_segments=24):
    verts = []
    faces = []
    for i in range(lat_segments + 1):
        theta = math.pi * i / lat_segments
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        for j in range(lon_segments):
            phi = 2 * math.pi * j / lon_segments
            x = radius * sin_t * math.cos(phi)
            y = radius * cos_t
            z = radius * sin_t * math.sin(phi)
            verts.append((x,y,z))
    def idx(i,j):
        return i*lon_segments + j + 1
    for i in range(lat_segments):
        for j in range(lon_segments):
            a = idx(i,j)
            b = idx(i,j+1 if j+1<lon_segments else 0)
            c = idx(i+1,j+1 if j+1<lon_segments else 0)
            d = idx(i+1,j)
            faces.append((a,b,c,d))
    return verts, faces


def generate_cylinder(radius=1.0, height=2.0, segments=24):
    verts = []
    faces = []
    h = height / 2.0
    for y in (-h, h):
        for i in range(segments):
            theta = 2*math.pi*i/segments
            verts.append((radius*math.cos(theta), y, radius*math.sin(theta)))
    # top and bottom faces
    top_center = (0, h, 0)
    bottom_center = (0, -h, 0)
    verts.append(top_center)
    verts.append(bottom_center)
    top_center_idx = len(verts)-1
    bottom_center_idx = len(verts)
    # side faces
    for i in range(segments):
        a = i+1
        b = i+1+segments
        c = (i+1+1)%segments + 1 + segments
        d = (i+1+1)%segments + 1
        faces.append((a,b,c,d))
    # caps
    # top cap uses vertices [segments+1 .. segments*2]
    for i in range(segments):
        a = segments + i + 1
        b = segments + ((i+1)%segments) + 1
        faces.append((top_center_idx+1, a, b))
    # bottom cap
    for i in range(segments):
        a = ((i+1)%segments) + 1
        b = i + 1
        faces.append((bottom_center_idx+1, a, b))
    return verts, faces


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--type', choices=['cube','uv_sphere','cylinder'], default='cube')
    p.add_argument('--size', type=float, default=1.0)
    p.add_argument('--radius', type=float, default=1.0)
    p.add_argument('--height', type=float, default=2.0)
    p.add_argument('--out', type=str, default='assets/models/sample_cube.obj')
    args = p.parse_args()

    if args.type == 'cube':
        verts, faces = generate_cube(size=args.size)
    elif args.type == 'uv_sphere':
        verts, faces = generate_uv_sphere(radius=args.radius)
    else:
        verts, faces = generate_cylinder(radius=args.radius, height=args.height)

    write_obj(verts, faces, args.out)
    print('Wrote', args.out)

if __name__ == '__main__':
    main()
