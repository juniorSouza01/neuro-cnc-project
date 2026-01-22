namespace NeuroEdge.Safety
{
    public static class SafetyGuard
    {
        // Limites duros. Nenhuma IA pode ultrapassar isso.
        private const double MAX_STEP_CHANGE = 0.050; // 50 microns
        private const double MAX_TOTAL_OFFSET = 0.300; // 3 décimos

        public static bool IsSafe(double adjustment)
        {
            if (System.Math.Abs(adjustment) > MAX_STEP_CHANGE) return false;
            // Aqui você adicionaria verificação do valor absoluto lendo a máquina
            return true;
        }
    }
}