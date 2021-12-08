import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name="fast_json_server",
    version="0.0.1",
    scripts=['fast_json_server/rest_api.py', 'fast_json_server/graph_ql.py',
             'fast_json_server/json_server.py'],
    author="Sai Kumar Yava",
    description="fast-json-server provides a full REST API / GraphQL Server with zero coding in few seconds.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/scionoftech/fast-json-server",
    packages=['fast_json_server'],
    keywords=['fastapi', 'json', 'json server', 'fake server', 'graphql'],
    install_requires=["pandas", "fastapi", "uvicorn", "graphene",
                      "click", "python-multipart", "async-exit-stack",
                      "async-generator"],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
    ],

)
# packages=setuptools.find_packages(include=['lib', 'lib.*', 'frames']),
# package_data = {'': ['*.py', 'lib/*']},
# include_package_data = True,
# data_files = [('lib/*')],
