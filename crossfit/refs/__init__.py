from pathlib import Path

__filepath = Path(__file__)
bin_dir = (__filepath.parent.parent / r'bin')
tools_dir = (bin_dir / r'tools')
deps_dir = (bin_dir / r'deps')

__all__ = ['bin_dir', 'tools_dir', 'deps_dir']
