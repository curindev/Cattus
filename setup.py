#from distutils.core import setup  
from setuptools import setup
  
setup(name="Cattus",  
      version="1.0",  
      description="Small sqlite3 visualizer",  
      author="Jose Francisco Franco Curin",  
      author_email="curindev18@gmail.com",  
      url="https://github.com/FranciscoCurin/Cattus",  
      license="GPL3",  
      scripts=["cattus"],  
      packages=["widget"],  
      install_requires=["python3-gi", "python3-gi-cairo", "libgtksourceview-3.0-1", "libgtksourceview-3.0-common", "libgtk-3-0", "python3-sqlparse", "python3-xlsxwriter"],
      
      data_files = [
        ('lib/cattus/ui/', ['ui/org.cattus.about.ui']),
        ('lib/cattus/ui/', ['ui/org.cattus.browser.ui']),      
        ('lib/cattus/ui/', ['ui/org.cattus.editor.ui']),
        ('lib/cattus/ui/', ['ui/org.cattus.export.ui']),
        ('lib/cattus/ui/', ['ui/org.cattus.remove.ui']),
        ('lib/cattus/ui/', ['ui/org.cattus.structure.ui']),
        ('lib/cattus/ui/', ['ui/org.cattus.window.ui']),   
        
        ('share/cattus/icon/', ['icon/org.cattus.add.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.buffer.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.clean.svg']),                
        ('share/cattus/icon/', ['icon/org.cattus.close.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.execute.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.export.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.format.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.open.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.operationok.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.refresh.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.remove.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.save.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.saveas.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.tabclose.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.tabnew.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.welcome.svg']),                                                                
        ('share/cattus/icon/', ['icon/org.cattus.icon.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.icon22.svg']),
        ('share/cattus/icon/', ['icon/org.cattus.icon32.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.icon48.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.iconscalable.svg']),        
        ('share/cattus/icon/', ['icon/org.cattus.logo.svg']),        
        
        ('share/applications/', ['cattus.desktop'])                
        ],
)  
