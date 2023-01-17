# Run yolov5 on dir
import torch
import numpy as np
from torchvision.utils import draw_keypoints
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union
from PIL import Image, ImageColor, ImageDraw, ImageFont
import platform

@dataclass
class ImageOverlay:
    path: str = ''
    location: str = ''
    image: list = field(default_factory=None)

    def __init__(self, path, image, location) -> None:
        self.path = path
        self.location = location
        self.image = image

def generate_overlay_QR_add(image_bboxes, bbox, labels_list, colors_list):
    current_os = platform.system()
    # print("OS in my system : ",current_os)
    if current_os == 'Linux':
        font_pick = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    elif current_os == 'Windows':
        font_pick = 'arial.ttf'
    elif current_os == 'Darwin':
        font_pick = '/Library/Fonts/Verdana/Verdana Regular.ttf' #TODO Check this path
    else:
        font_pick = ''
    # draw bounding boxes with fill color
    if font_pick == '':
        image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=[labels_list], 
                                            colors=[colors_list], fill=False, font_size=16, text_color = (255,0,255))
    else:
        image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=[labels_list], 
                                            colors=[colors_list], fill=False, font = font_pick, font_size=16, text_color = (255,0,255))   
    return image_bboxes


def generate_overlay_add(image_bboxes, bbox, labels_list, colors_list, centers_corrected, Marker_Unknown, distance):
    current_os = platform.system()
    # print("OS in my system : ",current_os)
    if current_os == 'Linux':
        font_pick = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    elif current_os == 'Windows':
        font_pick = 'arial.ttf'
    elif current_os == 'Darwin':
        font_pick = '/Library/Fonts/Verdana/Verdana Regular.ttf' #TODO Check this path
    else:
        font_pick = ''
    # draw bounding boxes with fill color
    image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=[labels_list], colors=[colors_list], fill=True, font = font_pick, font_size=20, text_color = (255,0,255))  
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Unknown.translate_center_point]]), colors="white", radius=5)

    # Add one cm. box
    average_one_cm_distance = distance
    if average_one_cm_distance is not np.nan:
        label_1CM = [''.join(['1 CM = ',str(np.round(average_one_cm_distance,1)),' Pixels'])]
        label_10CM = [''.join(['10 CM = ',str(np.round(np.multiply(average_one_cm_distance, 10), 1)),' Pixels'])]
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            centers_corrected[0]-(np.divide(average_one_cm_distance,2)),
                                            centers_corrected[1]-(np.divide(average_one_cm_distance,2)),
                                            centers_corrected[0]+(np.divide(average_one_cm_distance,2)),
                                            centers_corrected[1]+(np.divide(average_one_cm_distance,2))]]),
                                            width=1,labels=label_1CM,colors=(255, 0, 0),fill =True,font = font_pick, font_size=20, text_color = (255, 0, 0))  

        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            centers_corrected[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            centers_corrected[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            centers_corrected[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            centers_corrected[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10))  
    return image_bboxes

def generate_overlay(path_overlay, image_name_jpg, average_one_cm_distance, image_bboxes, bbox, labels_list, colors_list, centers_corrected, Marker_Top_Left, Marker_Top_Right, Marker_Bottom_Right, Marker_Bottom_Left):
    current_os = platform.system()
    # print("OS in my system : ",current_os)
    if current_os == 'Linux':
        font_pick = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    elif current_os == 'Windows':
        font_pick = 'arial.ttf'
    elif current_os == 'Darwin':
        font_pick = '/Library/Fonts/Verdana/Verdana Regular.ttf' #TODO Check this path
    else:
        font_pick = ''
    # Unpack new center points
    Marker_Top_Left.translate_center_point, Marker_Top_Right.translate_center_point, Marker_Bottom_Right.translate_center_point, Marker_Bottom_Left.translate_center_point = centers_corrected[0], centers_corrected[1], centers_corrected[2], centers_corrected[3]

    # draw bounding boxes with fill color
    image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=labels_list, colors=colors_list, fill=True, font = font_pick, font_size=20, text_color = (20, 120, 10)) 

    # Add one cm. box
    if average_one_cm_distance is not np.nan:
        label_1CM = [''.join(['1 CM = ',str(np.round(average_one_cm_distance,1)),' Pixels'])]
        label_10CM = [''.join(['10 CM = ',str(np.round(np.multiply(average_one_cm_distance, 10), 1)),' Pixels'])]
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Top_Left.translate_center_point[0]-(np.divide(average_one_cm_distance,2)),
                                            Marker_Top_Left.translate_center_point[1]-(np.divide(average_one_cm_distance,2)),
                                            Marker_Top_Left.translate_center_point[0]+(np.divide(average_one_cm_distance,2)),
                                            Marker_Top_Left.translate_center_point[1]+(np.divide(average_one_cm_distance,2))]]),
                                            width=1,labels=label_1CM,colors=(255, 0, 0),fill =True,font = font_pick, font_size=20, text_color = (255, 0, 0)) 

        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Top_Right.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Top_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Top_Right.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Top_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Top_Left.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Top_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Top_Left.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Top_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Bottom_Right.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Bottom_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Bottom_Right.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Bottom_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Bottom_Left.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Bottom_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Bottom_Left.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Bottom_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[bottom_right_center]]), colors="blue", radius=20)
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[top_left_center]]), colors="red", radius=20)
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[top_right_center]]), colors="green", radius=20)
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[bottom_left_center]]), colors="yellow", radius=20)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Top_Left.translate_center_point]]), colors="blue", radius=5)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Top_Right.translate_center_point]]), colors="red", radius=5)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Bottom_Left.translate_center_point]]), colors="cyan", radius=5)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Bottom_Right.translate_center_point]]), colors="yellow", radius=5)

    # image_bboxes = ToPILImage()(image_bboxes)
    # image_bboxes.show()
    # image_bboxes.save(os.path.join(path_overlay, image_name_jpg))
    return image_bboxes

@torch.no_grad()
def draw_bounding_boxes_custom(
    image: torch.Tensor,
    boxes: torch.Tensor,
    labels: Optional[List[str]] = None,
    colors: Optional[Union[List[Union[str, Tuple[int, int, int]]], str, Tuple[int, int, int]]] = None,
    fill: Optional[bool] = False,
    width: int = 1,
    font: Optional[str] = None,
    font_size: int = 40,
    text_color: Optional[Union[List[Union[str, Tuple[int, int, int]]], str, Tuple[int, int, int]]] = None,
) -> torch.Tensor:

    """
    Draws bounding boxes on given image.
    The values of the input image should be uint8 between 0 and 255.
    If fill is True, Resulting Tensor should be saved as PNG image.

    Args:
        image (Tensor): Tensor of shape (C x H x W) and dtype uint8.
        boxes (Tensor): Tensor of size (N, 4) containing bounding boxes in (xmin, ymin, xmax, ymax) format. Note that
            the boxes are absolute coordinates with respect to the image. In other words: `0 <= xmin < xmax < W` and
            `0 <= ymin < ymax < H`.
        labels (List[str]): List containing the labels of bounding boxes.
        colors (color or list of colors, optional): List containing the colors
            of the boxes or single color for all boxes. The color can be represented as
            PIL strings e.g. "red" or "#FF00FF", or as RGB tuples e.g. ``(240, 10, 157)``.
            By default, random colors are generated for boxes.
        fill (bool): If `True` fills the bounding box with specified color.
        width (int): Width of bounding box.
        font (str): A filename containing a TrueType font. If the file is not found in this filename, the loader may
            also search in other directories, such as the `fonts/` directory on Windows or `/Library/Fonts/`,
            `/System/Library/Fonts/` and `~/Library/Fonts/` on macOS.
        font_size (int): The requested font size in points.

    Returns:
        img (Tensor[C, H, W]): Image Tensor of dtype uint8 with bounding boxes plotted.
    """

    # if not torch.jit.is_scripting() and not torch.jit.is_tracing():
    #     _log_api_usage_once(draw_bounding_boxes)
    if not isinstance(image, torch.Tensor):
        raise TypeError(f"Tensor expected, got {type(image)}")
    elif image.dtype != torch.uint8:
        raise ValueError(f"Tensor uint8 expected, got {image.dtype}")
    elif image.dim() != 3:
        raise ValueError("Pass individual images, not batches")
    elif image.size(0) not in {1, 3}:
        raise ValueError("Only grayscale and RGB images are supported")

    num_boxes = boxes.shape[0]

    if labels is None:
        labels: Union[List[str], List[None]] = [None] * num_boxes  # type: ignore[no-redef]
    elif len(labels) != num_boxes:
        raise ValueError(
            f"Number of boxes ({num_boxes}) and labels ({len(labels)}) mismatch. Please specify labels for each box."
        )

    # if colors is None:
    #     colors = _generate_color_palette(num_boxes)
    elif isinstance(colors, list):
        if len(colors) < num_boxes:
            raise ValueError(f"Number of colors ({len(colors)}) is less than number of boxes ({num_boxes}). ")
    else:  # colors specifies a single color for all boxes
        colors = [colors] * num_boxes

    colors = [(ImageColor.getrgb(color) if isinstance(color, str) else color) for color in colors]

    # Handle Grayscale images
    if image.size(0) == 1:
        image = torch.tile(image, (3, 1, 1))

    ndarr = image.permute(1, 2, 0).cpu().numpy()
    img_to_draw = Image.fromarray(ndarr)
    img_boxes = boxes.to(torch.int64).tolist()

    if fill:
        draw = ImageDraw.Draw(img_to_draw, "RGBA")
    else:
        draw = ImageDraw.Draw(img_to_draw)

    txt_font = ImageFont.load_default() if font is None else ImageFont.truetype(font=font, size=font_size)

    for bbox, color, label in zip(img_boxes, colors, labels):  # type: ignore[arg-type]
        if fill:
            fill_color = color + (100,)
            draw.rectangle(bbox, width=width, outline=color, fill=fill_color)
        else:
            draw.rectangle(bbox, width=width, outline=color)

        if label is not None:
            if width == 1:
                margin = 24
            else:
                margin = np.multiply(2,(width + 2))
            draw.text((bbox[0], bbox[1] - margin), label, fill=text_color, font=txt_font)

    return torch.from_numpy(np.array(img_to_draw)).permute(2, 0, 1).to(dtype=torch.uint8)