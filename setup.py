from distutils.core import setup, Extension

def main():
    setup(name="ccollision",
          version="1.0.0",
          description="stub",
          author="Antony1060",
          author_email="antony@antony.red",
          ext_modules=[Extension("ccolission_s", ["ccollision.c"])])

if __name__ == "__main__":
    main()
