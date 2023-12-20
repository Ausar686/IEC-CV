import cv2
import os
import glob

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(directory + '/images'):
        os.makedirs(directory + '/images')
    if not os.path.exists(directory + '/labels'):
        os.makedirs(directory + '/labels')

def draw_labels(image_path, img):
    label_file = image_path.replace('images', 'labels').replace('.jpg', '.txt').replace('.png', '.txt')
    if os.path.exists(label_file):
        with open(label_file, 'r') as file:
            lines = file.readlines()
            h, w, _ = img.shape
            for line in lines:
                _, x_center, y_center, width, height = map(float, line.split())
                x_center, y_center, width, height = x_center * w, y_center * h, width * w, height * h
                x1, y1, x2, y2 = int(x_center - width / 2), int(y_center - height / 2), int(x_center + width / 2), int(y_center + height / 2)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

def main(folder_path, accepted_folder, rejected_folder):
    create_directory_if_not_exists(accepted_folder)
    create_directory_if_not_exists(rejected_folder)
    
    image_paths = glob.glob(os.path.join(folder_path, 'images', '*.jpg'))

    for image_path in image_paths:
        img = cv2.imread(image_path)
        draw_labels(image_path, img)
        cv2.imshow('Image', img)

        key = cv2.waitKey(0)
        if key == ord('d'):
            # Move to accepted folder
            label_path = image_path.replace(f'{os.sep}images{os.sep}', f'{os.sep}labels{os.sep}').replace('.jpg', '.txt').replace('.png', '.txt')
            os.rename(image_path, os.path.join(accepted_folder, 'images', os.path.basename(image_path)))
            os.rename(label_path, os.path.join(accepted_folder, 'labels', os.path.basename(label_path)))
        elif key == ord('a'):
            # Move to rejected folder
            label_path = image_path.replace(f'{os.sep}images{os.sep}', f'{os.sep}labels{os.sep}').replace('.jpg', '.txt').replace('.png', '.txt')
            os.rename(image_path, os.path.join(rejected_folder, 'images', os.path.basename(image_path)))
            os.rename(label_path, os.path.join(rejected_folder, 'labels', os.path.basename(label_path)))
        elif key == ord('q'):
            return

    cv2.destroyAllWindows()

if __name__ == "__main__":
    folder_path = 'test'
    accepted_folder = 'accepted'
    rejected_folder = 'rejected'
    main(folder_path, accepted_folder, rejected_folder)
