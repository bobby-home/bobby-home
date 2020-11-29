# Alarm

## Define region of interests

### Camera Rectangle
When the resident wants to update its Camera Rectangle ROI's, the system doesn't update `CameraRectangleROI` objects. The system disables all `CameraRectangleROI` to create news.

Why? Because it makes everything easier, especially the UI. It should not impact badly the performance because this feature won't have thousands of `CameraRectangleROI`, maybe 2-3 max!
