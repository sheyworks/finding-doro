using UnityEngine;

public class CoinSpin : MonoBehaviour
{
    [SerializeField] private float rotationSpeed = 30f;

    private void Update()
    {
        transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime, Space.Self);
    }
}
