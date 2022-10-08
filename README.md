# Thumbnails in a Pinch
For my first freelance gig, I didn't setup automatic thumbnails on Firebase, when all of a sudden, we already had 88 images in our storage bucket, and they were massive. I tried creating a Cloud Function to make the thumbnails, but I found out that was probably not a good idea. 

I used the gcloud console to download all the images into a local folder, and created this little Python program to do the magic.

It's a very simple program. It uses the Pillow library to create the thumbnails. Most of the parameters are hardcoded, so use with care. 

