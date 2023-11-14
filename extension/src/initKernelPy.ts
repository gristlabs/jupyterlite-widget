function code() {
  const packageUrl = new URL('../files/package.tar.gz', window.location.href).href;

  // language=Python
  return `
async def __bootstrap_grist(url):
    from pyodide.http import pyfetch  # noqa
    import io
    import tarfile
    
    response = await pyfetch(url)
    bytes_file = io.BytesIO(await response.bytes())
    with tarfile.open(fileobj=bytes_file) as tar:
        tar.extractall()
    
    import grist.browser  # noqa
    return grist.browser.grist

grist = await __bootstrap_grist(${JSON.stringify(packageUrl)})
`;
}

export default code;
