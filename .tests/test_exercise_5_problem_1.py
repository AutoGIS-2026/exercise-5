"""Basic checks for exercise 5, problem 1 (static map). Graded manually: no points."""

import PIL.Image

from points_decorator import points


MIN_COLOURS = 16  # a map has many colours, an empty figure only a few
MIN_SIZE = 600  # pixels (matplotlib’s default figure is 640×480)


def png_files(output_directory):
    return sorted(output_directory.glob("*.png"))


class TestProblem1:
    @points(0, "Problem 1: Save your static map as a PNG file in the `docs` folder, and add, commit and push it.")
    def test_png_file_exists(self, output_directory):
        assert png_files(output_directory)

    @points(0, "Problem 1: A PNG file in `docs` could not be opened as an image.")
    def test_png_files_are_images(self, output_directory):
        files = png_files(output_directory)
        assert files
        for png_file in files:
            with PIL.Image.open(png_file) as image:
                image.verify()

    @points(0, "Problem 1: Your PNG map seems to be (almost) empty.")
    def test_png_not_blank(self, output_directory):
        files = png_files(output_directory)
        assert files
        for png_file in files:
            with PIL.Image.open(png_file) as image:
                colours = image.convert("RGB").getcolors(maxcolors=MIN_COLOURS)
            # getcolors() returns None if there are more than `maxcolors` colours
            assert colours is None

    @points(0, f"Problem 1: Your PNG map is quite small (less than {MIN_SIZE} pixels wide and high). Consider increasing the figure size or `dpi`.")
    def test_png_resolution(self, output_directory):
        files = png_files(output_directory)
        assert files
        for png_file in files:
            with PIL.Image.open(png_file) as image:
                assert max(image.size) >= MIN_SIZE

    @points(0, "Problem 1: Add, commit and push the code you used to create your map to `Exercise-5-problem-1.ipynb`.")
    def test_notebook_has_code(self, problem1_code):
        assert len(problem1_code) >= 5
