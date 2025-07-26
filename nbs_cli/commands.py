#!/usr/bin/env python3

#############################################################################################################################################################################
#   The license used for this file and its contents is: BSD-3-Clause                                                                                                        #
#                                                                                                                                                                           #
#   Copyright <2025> <Uri Herrera <uri_herrera@nxos.org>>                                                                                                                   #
#                                                                                                                                                                           #
#   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:                          #
#                                                                                                                                                                           #
#    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.                                        #
#                                                                                                                                                                           #
#    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer                                      #
#       in the documentation and/or other materials provided with the distribution.                                                                                         #
#                                                                                                                                                                           #
#    3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software                    #
#       without specific prior written permission.                                                                                                                          #
#                                                                                                                                                                           #
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,                      #
#    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS                  #
#    BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE                 #
#    GOODS OR SERVICES; LOSS OF USE, DATA,   OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,                      #
#    STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.   #
#############################################################################################################################################################################

import typer
import yaml
from pathlib import Path
from rich.console import Console

from nbs_cli.orchestrator import create_base_system
# <---
# --->
console = Console()

def build(config: Path = typer.Argument(..., exists=True, help="Path to the YAML config file")):
    """
    🔧 Build a base root filesystem from a package list and repositories.
    """
    console.rule("[bold green]🧰 Nitrux Bootstrap System")

    try:
        with config.open() as f:
            data = yaml.safe_load(f)
            repos = data["buildinfo"]["distrorepo"]
            packages = data.get("base", [])
            if not packages:
                typer.secho("⛔ No base packages defined.", fg=typer.colors.RED)
                raise typer.Exit(1)
    except yaml.YAMLError as e:
        typer.secho(f"⛔ YAML parsing failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
    except KeyError:
        typer.secho("⛔ Invalid YAML: Missing 'buildinfo.distrorepo'", fg=typer.colors.RED)
        raise typer.Exit(1)

    summary = create_base_system(packages, repos)

    console.rule("[bold blue]📊 Build Summary")
    typer.secho(f"✅ Success: {summary['success']}", fg=typer.colors.GREEN)
    console.print("")
    typer.secho(f"⛔ Failed: {summary['failed']}", fg=typer.colors.RED)
    console.print("")
    typer.secho(f"⚠ Skipped: {summary['skipped']}", fg=typer.colors.YELLOW)
    console.print("")


def hello():
    """Simple hello command to demonstrate multi-command interface."""
    typer.echo("Hello, world!")
