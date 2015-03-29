import git
import os
from annoying.decorators import render_to

from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from .models import VideoFile
from kalite.control_panel.views import local_install_context
from kalite.i18n import get_installed_language_packs
from kalite.shared.decorators.auth import require_admin
from securesync.models import Device
from securesync.devices import require_registration


def update_context(request):
    device = Device.get_own_device()
    zone = device.get_zone()

    context = {
        "is_registered": device.is_registered(),
        "zone_id": zone.id if zone else None,
        "device_id": device.id,
    }
    return context


@require_admin
@require_registration(_("video downloads"))
@render_to("updates/update_videos.html")
def update_videos(request, max_to_show=4):
    context = update_context(request)
    messages.warning(request, _('For low-powered devices like the Raspberry Pi, please download videos one at a time.'))
    context.update({
        "video_count": VideoFile.objects.filter(percent_complete=100).count(),
    })
    return context


@require_admin
@require_registration(_("language packs"))
@render_to("updates/update_languages.html")
def update_languages(request):
    # also refresh language choices here if ever updates js framework fails, but the language was downloaded anyway
    installed_languages = get_installed_language_packs(force=True)

    # here we want to reference the language meta data we've loaded into memory
    context = update_context(request)
    context.update({
        "installed_languages": installed_languages.values(),
    })
    return context


@require_admin
@render_to("updates/update_software.html")
def update_software(request):
    context = update_context(request)
    context.update(local_install_context(request))

    try:
        repo = git.Repo(os.path.dirname(__file__))
        software_version = repo.git.describe()
        is_git_repo = bool(repo)
    except git.exc.InvalidGitRepositoryError:
        is_git_repo = False
        software_version = None

    context.update({
        "is_git_repo": str(is_git_repo).lower(), # lower to make it look like JS syntax
        "git_software_version": software_version,
    })

    return context
