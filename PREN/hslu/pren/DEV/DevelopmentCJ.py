
from hslu.pren.visuals import ContainerDetection


if __name__ == '__main__':
    
    detector = ContainerDetection.ContainerDetector()
    
    container = detector.CheckContainer(True, 10000)
    
    pass