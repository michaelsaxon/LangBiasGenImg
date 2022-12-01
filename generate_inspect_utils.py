import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from typing import Callable, List, Optional, Union


# external implementation of the first two steps of the generation pipeline for stable diffusion
# STEP 1: GET EMBEDDINGS
def get_text_embs(
    model: StableDiffusionPipeline,         
    prompt: Union[str, List[str]],
    guidance_scale: float = 7.5,
    negative_prompt: Optional[Union[str, List[str]]] = None,
    num_images_per_prompt: Optional[int] = 1,
):

    if not isinstance(prompt, str) and not isinstance(prompt, list):
        raise ValueError(f"`prompt` has to be of type `str` or `list` but is {type(prompt)}")

    # 2. Define call parameters
    batch_size = 1 if isinstance(prompt, str) else len(prompt)
    device = model._execution_device
    # here `guidance_scale` is defined analog to the guidance weight `w` of equation (2)
    # of the Imagen paper: https://arxiv.org/pdf/2205.11487.pdf . `guidance_scale = 1`
    # corresponds to doing no classifier free guidance.
    do_classifier_free_guidance = guidance_scale > 1.0

    # 3. Encode input prompt
    return model._encode_prompt(
        prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt
    )

# external implementation of the first two steps of the generation pipeline for stable diffusion
# STEP 2: GET LATENTS
def get_latents(
    model: StableDiffusionPipeline,         
    prompt: Union[str, List[str]],
    height: Optional[int] = None,
    width: Optional[int] = None,
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5,
    negative_prompt: Optional[Union[str, List[str]]] = None,
    num_images_per_prompt: Optional[int] = 1,
    generator: Optional[torch.Generator] = None,
    latents: Optional[torch.FloatTensor] = None,
    callback_steps: Optional[int] = 1,
):

    # 0. Default height and width to unet
    height = height or model.unet.config.sample_size * model.vae_scale_factor
    width = width or model.unet.config.sample_size * model.vae_scale_factor

    # 1. Check inputs. Raise error if not correct
    model.check_inputs(prompt, height, width, callback_steps)

    batch_size = 1 if isinstance(prompt, str) else len(prompt)
    device = model._execution_device

    text_embeddings = get_text_embs(model, prompt, guidance_scale, negative_prompt, num_images_per_prompt)
    # 4. Prepare timesteps
    model.scheduler.set_timesteps(num_inference_steps, device=device)
    timesteps = model.scheduler.timesteps

    # 5. Prepare latent variables
    num_channels_latents = model.unet.in_channels
    latents = model.prepare_latents(
        batch_size * num_images_per_prompt,
        num_channels_latents,
        height,
        width,
        text_embeddings.dtype,
        device,
        generator,
        latents,
    )

    return latents


'''
def get_generate():
    prompt = input("Prompt:\n").strip().lower()
    with autocast("cuda"):
        image = pipe(prompt, guidance_scale=7.5, num_images_per_prompt=9).images
    for i, im in enumerate(image):
        print(f"done generating {prompt.replace(' ','')}_{i}.png")
        im.save(f"playground/{prompt.replace(' ','')}_{i}.png")
'''


def main():
    model_id = "CompVis/stable-diffusion-v1-4"
    device = "cuda"

    pipe = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=True)
    pipe = pipe.to(device)
