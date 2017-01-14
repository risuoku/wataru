{
    "display_name": "{{ kernel_display_name }}", 
    "language": "python", 
    "argv": [
        "python", 
        "-m", "ipykernel",
        "--profile={{ kernel_argv_profile }}",
        "-f", "{connection_file}"
    ]
}
