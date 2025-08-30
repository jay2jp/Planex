# `pubspec.yaml` Changes

The `pubspec.yaml` file was modified to include the image assets required for the login page.

## Asset Changes

The following line was added to the `flutter` section to include the images in the `assets/images/` directory:

```yaml
flutter:
  uses-material-design: true
  assets:
    - .env
    - assets/images/
```

This allows the application to use images like the logo and icons for the login buttons.