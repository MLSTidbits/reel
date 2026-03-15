<div align="center">
  <img src="images/logo.svg"
  alt="Reel - DVD and Blu-ray Ripping Tool"
  width="auto"
  height="256px" />
  <p>
    Backup and rip your DVD and Blu-ray collection with ease using Reel.
  </p>
  <p>  </p>
  <p>  </p>
  <p>  </p>
  <image src="images/demo.gif" alt="Reel in action" width="auto" height="360px" />
</div>

## ABOUT

**Reel**  uses the [MakeMKV](https://www.makemkv.com/) command-line interface to rip DVDs and Blu-rays. It provides a simple and intuitive interface for selecting the source, destination, and ripping options. This is possible thanks to the `/usr/bin/makemkvcon` which is included in the with the [Tarball](https://www.makemkv.com/download/makemkv-bin-1.18.3.tar.gz) from MakeMKV.

## FEATURES

- **Easy to Use**: Reel provides a user-friendly interface for ripping your DVDs and Blu-rays, making it accessible to users of all technical levels.
- **Automatic Detection**: Automatically detects when a DVD or Blu-ray a is inserted.
- **Control MakeMKV**: Define both **REEL** and **MakeMKV** preferences to customize your ripping experience.
- **Logging**: Real-time logging of the ripping process, allowing you to monitor progress and troubleshoot any issues that may arise.
- **Rename Files**: Allows you to rename the output files, great for organizing your media library.

## INSTALLATION

### Debian-based Systems

On Debian-based systems, you can install Reel using the following commands by going to the [MLS Tidbits repository](https://archive.mlstidbits.com/). Once thee repository is added, you can install Reel with:

```bash
sudo apt update
# For GTK version
sudo apt install --yes reel-gtk
# For Qt version
sudo apt install --yes reel-qt
```

### Other Systems

For other systems, clone the repository and install with:

```bash
git clone https://github.com/MLSTidbits/reel.git
cd reel
# For GTK version
sudo make && sudo make install GTK_INSTALL=enable
# For Qt version
sudo make && sudo make install QT_INSTALL=enable
```

If both versions are specified, then neither will be installed and an error will be thrown.

## CONCLUSION

Reel is a powerful and user-friendly tool for ripping DVDs and Blu-rays using the MakeMKV command-line interface. With its intuitive interface and robust features, Reel makes it easy to backup and organize your media collection. Whether you're a casual user or a media enthusiast, Reel provides a seamless ripping experience.

This project came about as a way to have a simple and efficient tool for ripping DVDs and Blu-rays without an application that blends in with the desktop environment. By using the MakeMKV command-line interface, Reel offers a lightweight and customizable solution for users who want to manage their media library with ease.

## CONTRIBUTING

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository. If you would like to contribute code, please fork the repository and create a pull request.

## LICENSE

MakeMKV (c) 2008-2025 EULA GuinpinSoft Inc. All rights reserved.

libmakemkv (c) 2008-2025 LGPLv2.1+ EULA GuinpinSoft Inc. All rights reserved.

Reel (c) 2026 GPLv3+ MLS Tidbits. All rights reserved.
