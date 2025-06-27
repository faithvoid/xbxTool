import struct
import os
import sys

def extract_xpr0_raw_texture(xbx_path):
    with open(xbx_path, "rb") as f:
        data = f.read()

    if data[:4] != b'XPR0':
        raise ValueError("Not an XPR0 file.")

    file_size = struct.unpack_from("<I", data, 4)[0]
    header_size = struct.unpack_from("<I", data, 8)[0]
    data_offset = header_size

    print(f"[INFO] File size: {file_size}, Header size: {header_size}, Data offset: {data_offset}")
    raw_data = data[data_offset:]
    return raw_data

def create_dds_header(width, height, dxt_format, data_size):
    DDSD_CAPS = 0x00000001
    DDSD_HEIGHT = 0x00000002
    DDSD_WIDTH = 0x00000004
    DDSD_PIXELFORMAT = 0x00001000
    DDSD_LINEARSIZE = 0x00080000

    DDPF_FOURCC = 0x00000004
    DDSCAPS_TEXTURE = 0x00001000

    header = b'DDS '
    header += struct.pack('<I', 124)                            # dwSize
    header += struct.pack('<I', DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_LINEARSIZE)
    header += struct.pack('<I', height)                         # dwHeight
    header += struct.pack('<I', width)                          # dwWidth
    header += struct.pack('<I', data_size)                      # dwPitchOrLinearSize
    header += struct.pack('<I', 0)                              # dwDepth
    header += struct.pack('<I', 0)                              # dwMipMapCount
    header += b'\x00' * 44                                      # dwReserved1

    # DDS_PIXELFORMAT (32 bytes)
    header += struct.pack('<I', 32)                             # dwSize
    header += struct.pack('<I', DDPF_FOURCC)                    # dwFlags
    header += dxt_format.encode('utf-8').ljust(4, b'\x00')      # dwFourCC
    header += struct.pack('<I', 0) * 5                          # rest unused

    header += struct.pack('<I', DDSCAPS_TEXTURE)               # dwCaps1
    header += struct.pack('<I', 0) * 3                          # dwCaps2–4
    header += struct.pack('<I', 0)                              # dwReserved2

    return header


def convert_xbx_to_dds(xbx_path, width=256, height=256, dxt_format="DXT1", output_dir=None):
    try:
        raw_texture = extract_xpr0_raw_texture(xbx_path)
        dds_header = create_dds_header(width, height, dxt_format, len(raw_texture))
        dds_data = dds_header + raw_texture

        base_name = os.path.splitext(os.path.basename(xbx_path))[0]
        dds_filename = base_name + ".dds"
        if output_dir is None:
            output_dir = os.path.dirname(xbx_path)
        out_path = os.path.join(output_dir, dds_filename)

        with open(out_path, "wb") as f:
            f.write(dds_data)

        print(f"[SUCCESS] DDS saved to: {out_path}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xbx_to_dds.py <file.xbx> [width height format] [output_dir]")
        sys.exit(1)

    xbx_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 256
    height = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    dxt_format = sys.argv[4] if len(sys.argv) > 4 else "DXT1"
    output_dir = sys.argv[5] if len(sys.argv) > 5 else None

    convert_xbx_to_dds(xbx_path, width, height, dxt_format, output_dir)
