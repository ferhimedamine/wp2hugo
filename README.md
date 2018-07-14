wp2hugo
=======
Tools to migrate from Wordpress.com to Hugo



## Usage

1. Downnload all images.

    ```bash
    python -m wp2hugo.download_images --input-file WORDPRESS_XML --output-dir HUGO_OUTPUT --name USER_NAME
    ```

2. Convert XML file.

    ```bash
    python -m wp2hugo.wp2hugo --input-file WORDPRESS_XML --output-dir HUGO_OUTPUT
    ```
