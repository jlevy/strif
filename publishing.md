## Publishing Releases

This is how to publish a Python package to [**PyPI**](https://pypi.org/) from GitHub
Actions, when using the
[**simple-modern-uv**](https://github.com/jlevy/simple-modern-uv) template.

Thanks to [the dynamic versioning
plugin](https://github.com/ninoseki/uv-dynamic-versioning/) and the
[`publish.yml` workflow](https://github.com/jlevy/simple-modern-uv/blob/main/template/.github/workflows/publish.yml),
you can simply create tagged releases (using standard format for the tag name, e.g.
`v0.1.0`) on GitHub and the tag will trigger a release build, which then uploads it to
PyPI.

### How to Publish the First Time

This part is a little confusing the first time.
Here is the simplest way to do it.
For the purposes of this example replace OWNER and PROJECT with the right values.

1. **Get a PyPI account** at [pypi.org](https://pypi.org/) and sign in.

2. **Pick a name for the project** that isn't already taken.

   - Go to `https://pypi.org/project/PROJECT` to see if another project with that name
     already exits.

   - If needed, update your `pyproject.yml` with the correct name.

3. **Authorize** your repository to publish to PyPI:

   - Go to [the publishing settings page](https://pypi.org/manage/account/publishing/).

   - Find "Trusted Publisher Management" and register your GitHub repo as a new
     "pending" trusted publisher

   - Enter the project name, repo owner, repo name, and `publish.yml` as the workflow
     name. (You can leave the "environment name" field blank.)

4. **Create a release** on GitHub:

   - Commit code and make sure it's running correctly.

   - Go to your GitHub project page, then click on Actions tab.

   - Confirm all tests are passing in the last CI workflow.
     (If you want, you can even publish this template when it's empty as just a stub
     project, to try all this out.)

   - Go to your GitHub project page, click on Releases.

   - Fill in the tag and the release name.
     Select to create a new tag, and pick a version.
     A good option is `v0.1.0`. (It's wise to have it start with a `v`.)

   - Submit to create the release.

5. **Confirm it publishes to PyPI**

   - Watch for the release workflow in the GitHub Actions tab.

   - If it succeeds, you should see it appear at `https://pypi.org/project/PROJECT`.

### How to Publish Subsequent Releases

Just create a new release!
Everything is the same as the last two steps above.

* * *

*This file was built with
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
