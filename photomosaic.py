"""
OpenCV Image pixels are represented in (B, G, R) order
"""
import copy
import glob
import math
import numpy as np
import cv2

PATH_IMGBASE_FLAGS    = './imagebase-flags-w2560-h1706-jpeg/*.jpg'
PATH_IMAGEBASE_NATURE = './imagebase-nature-jpeg/*.jpg'
PATH_IMGBASE_JPEG = PATH_IMGBASE_FLAGS
IMAGE_BASE = glob.glob(PATH_IMGBASE_JPEG)
IMAGE_BASE = [ x.replace("\\", '/' ) for x in IMAGE_BASE ]

PATH_TEST_IMAGE  =  './test_images/test_image_3.jpg'
PATH_INPUT_IMAGE =  './img_input.jpg'

IMAGE_PATH = PATH_TEST_IMAGE

# -------------------------------------------------------------------- #

class PhotoMosaic():
    
    def __init__(self, img=None, imgbase=None):
        self.img = img
        self.imgbase = imgbase
        self.imgbase_ch_avg = []
        self.img_w = 7200
        self.img_h = 4800
        self.pixel_unit_w = 20
        self.pixel_unit_h = 20
        
    def resize_image(self, img, width=200, height=None):        
        if height is None:
            h, w = img.shape[:2]
            ratio = w / h
            dim = ( width, int(width/ratio) )
            img_resized = cv2.resize(img, dim)
        else:
            dim = (width, height)
            img_resized = cv2.resize(img, dim)
        return img_resized
    
    def resize_input_image(self, img):
        if ( ( img.shape[:2][0] < self.img_h ) and 
             ( img.shape[:2][1] < self.img_w ) ) :
               img_resized = img
        else:
            img_resized = self.resize_image(img, width=self.img_w, 
                                                 height=self.img_h)
        return img_resized
        
        
    def raise_value_error(self):
        raise ValueError("Pixel channel value must be in range 0-255")
    
    def blue_shift(self, img, B=None):
        if B is not None:
            if B in range(256):
                img[:,:,0] = B
            else:
                self.raise_value_error()
        return img
    
    def green_shift(self, img, G=None):
        if G is not None:
            if G in range(256):
                img[:,:,1] = G
            else:
                self.raise_value_error()
        return img
    
    def red_shift(self, img, R=255):
        if R is not None:
            if R in range(256):
                img[:,:,2] = R
            else:
                self.raise_value_error()
        return img
                
    def tint_shift(self, img, channel=None, value=None):
        match channel:
            case 'B':
                img = self.blue_shift(img,B=value)
            case 'G':
                img = self.green_shift(img,G=value)
            case 'R':
                img = self.red_shift(img,R=balue)
        return img
        
                
    def measure_channel_error(self, pixela, pixelb):
        channel_err = math.sqrt( 
        sum( 
        [ math.pow( 
          ( max(pixela[ch],pixelb[ch]) - min(pixela[ch],pixelb[ch])), 2 ) 
            for ch in range(3) ] 
        ) / 3.0 )
        
        
        return channel_err
    
    def measure_channel_avg(self, img):
        ch_b = img[:,:,0]
        ch_g = img[:,:,1]
        ch_r = img[:,:,2]
        
        h, w = img.shape[:2]
        
        ch_b_avg = sum( [ sum(ch_b[r,:]) for r in range(h) ] ) / (h*w)
        ch_g_avg = sum( [ sum(ch_g[r,:]) for r in range(h) ] ) / (h*w)
        ch_r_avg = sum( [ sum(ch_r[r,:]) for r in range(h) ] ) / (h*w)
        
        ch_avg = np.array( [int(ch_b_avg), int(ch_g_avg), int(ch_r_avg)],
                           dtype = np.uint8) 
        
        return ch_avg
    
    def process_imgbase(self, imgbase):            
        self.imgbase = [ self.resize_image(imgb, width=self.pixel_unit_w, 
                                                 height=self.pixel_unit_h) 
                         for imgb in imgbase ]        
        self.imgbase_ch_avg = [ self.measure_channel_avg(imgb)
                                for imgb in self.imgbase ]
        
        
    
    def pick_img_for_pixel_unit(self,pixel,imgbase):
        pixela = pixel
        min_ch_err = 255
        for i in range(len(imgbase)):            
            pixelb = self.imgbase_ch_avg[i]
            ch_err = self.measure_channel_error(pixela, pixelb)
            if ch_err < min_ch_err:
                min_ch_err = ch_err
                img_o = self.imgbase[i]
        return img_o
        
    
    def make_mosaic(self, img, imgbase):
        self.process_imgbase(imgbase)
        
        img = self.resize_input_image(img)
        
        h, w = img.shape[:2]
        
        img_cpy = copy.deepcopy(img)
        
        pixel_unit_w = self.pixel_unit_w
        pixel_unit_h = self.pixel_unit_h
        
        for r in range(0, h, pixel_unit_h):
            r_end = r + pixel_unit_h
            for c in range(0, w, pixel_unit_w):
                c_end = c + pixel_unit_w
                img_segment = img[r:r_end, c:c_end]
                pixela  = self.measure_channel_avg(img_segment)
                img_pix = self.pick_img_for_pixel_unit(pixela, self.imgbase)
                img_cpy[r:r_end, c:c_end] = img_pix   
        
        return img_cpy
        
    
# -------------------------------------------------------------------- #

if __name__=='__main__':
    
    WRITE_IMAGE = 1

    img = cv2.imread(IMAGE_PATH, flags=cv2.IMREAD_COLOR)
    imgbase = [ cv2.imread(imgpath, flags=cv2.IMREAD_COLOR) 
                for imgpath in IMAGE_BASE ]    
    
    phmosaic = PhotoMosaic()
    
    img_out = phmosaic.make_mosaic(img, imgbase)
    
    
    if WRITE_IMAGE:
        CNT = len(glob.glob('./test_images_output/*.jpg')) + 1
        IMAGE_OUTPUT = 'img_' + str(CNT) + '.jpg'
        PATH_TEST_IMAGE_OUTPUT = './test_images_output/' + IMAGE_OUTPUT
        cv2.imwrite(PATH_TEST_IMAGE_OUTPUT, img_out)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        