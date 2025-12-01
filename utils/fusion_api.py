from fusionbrain_sdk_python import AsyncFBClient, PipelineType
import base64
from config import FB_API_KEY, FB_SECRET_KEY


client = AsyncFBClient(x_key=FB_API_KEY, x_secret=FB_SECRET_KEY)

async def generate_pig_image(prompt):
    pipelines = await client.get_pipelines_by_type(PipelineType.TEXT2IMAGE)
    text2image_pipeline = pipelines[0]

    run_result = await client.run_pipeline(
        pipeline_id=text2image_pipeline.id,
        prompt=f"Сгенерируй свинью: {prompt}",
    )

    final_status = await client.wait_for_completion(
        request_id=run_result.uuid,
        initial_delay=run_result.status_time
    )

    if final_status.status == 'DONE':
        img_base64 = final_status.result.files[0]
        return base64.b64decode(img_base64)
    else:
        return None
    