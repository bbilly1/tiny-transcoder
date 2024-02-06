# Tiny Transcoder

![screenshot](/assets/screenshot.png)

## Core Functionality
- Transcode media using ffmpeg
- Optionally use hardware acceleration
- Dynamic queue management
- Progress monitor
- Built with Flask/React

## Assumptions
- This assumes that you already know the ffmpeg command you want to run on your collection. Maybe you want to reduce the CRF value, reduce bitrate or convert to x265.
- This is not meant to be run on *all* your media files, pick and choose what makes sense. Depending on your input file and your ffmpeg configuration, your ffmpeg command may or may not compress your files or will even have a degrading effect.
- This will default to *.mkv* format and will **overwrite** the original files you add to the queue. So when in doubt, test your configuration and run the transcode on a *copy* and not on the *original* file.

## Install
This is a docker container. Configure your volumes and environment variables as described below, there are compose examples further down. Help with adding additional instructions.

### Volumes
- `/data`: Application data volume to store the queue database
- `/media`: Root path for your media collection folder
- `/cache`: Temporary path to store the file while transcoding, should be on the same drive as `/media`.

### Environment Variables
- `TT_FFMPEG`: JSON formatted Key Value config pairs to be passed to ffmpeg.
- `TT_HWACCEL` (optional): Define method for hardware acceleration, e.g. `cuda`
- `TT_PORT` (optional): Overwrite the default port `8000`.

### Hardware acceleration
Resources to enable GPU support for a docker container, adjust to your environment:
- [Docker docs](https://docs.docker.com/compose/gpu-support/)
- [Arch Wiki](https://wiki.archlinux.org/title/Docker#Run_GPU_accelerated_Docker_containers_with_NVIDIA_GPUs)

### Compose Examples
Contribute to add additional hardware configurations.

<details>
<summary>Basic without hardware support</summary>

```yml
version: '3.5'

services:
  tiny-transcoder:
    container_name: tiny-transcoder
    restart: unless-stopped
    image: bbilly1/tiny-transcoder
    volumes:
      - /media/docker/tiny-transcoder:/data
      - /media/mount/cache:/cache
      - /media/mount:/media
    ports:
      - 127.0.0.1:8000:8000
    environment:
      TT_FFMPEG: '{"c:v": "libx265", "crf": 23, "preset": "slow", "vf": "scale=-1:1080"}'
```

</details>

<details>
<summary>CUDA Nvidia GPU</summary>

```yml
version: '3.5'

services:
  tiny-transcoder:
    container_name: tiny-transcoder
    restart: unless-stopped
    image: bbilly1/tiny-transcoder
    volumes:
      - /media/docker/tiny-transcoder:/data
      - /media/mount/cache:/cache
      - /media/mount:/media
    ports:
      - 127.0.0.1:8000:8000
    environment:
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: gpu,video
      TT_HWACCEL: cuda
      TT_FFMPEG: '{"c:v": "hevc_nvenc", "crf": 23, "preset": "slow", "vf": "scale=-1:1080"}'
    deploy:
      resources:
   	 reservations:
 		 devices:
 		 - driver: nvidia
   		 capabilities:
     		 - gpu
     		 - video
```

</details>

## Update
The queue is meant to be transient, clear the queue regularly, keep your queue to a manageable size. There probably won't be a migration path for your database. Check the release notes if you have to clear your `queue.db`.

## Usage

### Add to Queue
Click on the *add* icon to open a form to add media files to your queue. Click on the add icon again, to hide the form.

**Absolute/relative**: If you add an absolute path, make sure to prefix that with `/media`, as the path is absolute from *inside* the container. If you add a relative path that will be relative from the `/media` folder.

**Folder/file**: You can add a folder to the queue to add all files of the folder. Make sure there are only media files in the folder. That is not recursive. Or add file by file.

### Start Queue
If you have any files in the queue, a *start* icon will show to start the queue. That will run the queue until there are no more pending items.

### Delete Queue
Click on the *delete* icon to show options to delete the queue. You can delete by state **pending**, **paused**, **completed**, or delete **all**. Click on the *delete* icon again to hide the options.

## Credits
This is very much inspired by the superior [Tdarr](https://github.com/HaveAGitGat/Tdarr/) project and is a less complex, less feature rich, *tiny* project to transcode your media.
