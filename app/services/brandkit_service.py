BRANDKITS = {

    "1":{
        "brand_name":"BrandFlow",
        "tagline":"Design Faster",
        "logo":"logo.png",
        "colors":["#2563EB","#9333EA"],
        "headline_font":"Inter-Bold.ttf",
        "sub_font":"Inter-Regular.ttf"
    }

}

def get_brandkit(brandkit_id):

    return BRANDKITS.get(brandkit_id)